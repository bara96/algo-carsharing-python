from algosdk import account
from algosdk import logic as algo_logic
from algosdk.encoding import decode_address
from pyteal import compileTeal, Mode

from smart_contracts.contract_carsharing import CarSharingContract
from smart_contracts.contract_escrow import contract_escrow
from helpers import algo_helper
from models.ApplicationManager import ApplicationManager
from utilities import utils, account_utils


class Trip:
    CREATOR_FIELD = 'creator'
    CREATOR_NAME_FIELD = 'creator_name'
    DEPARTURE_ADDRESS_FIELD = 'departure_address'
    ARRIVAL_ADDRESS_FIELD = 'arrival_address'
    DEPARTURE_DATE_FIELD = 'departure_date'
    ARRIVAL_DATE_FIELD = 'arrival_date'
    AVAILABLE_SEATS_FIELD = 'available_seats'
    TRIP_COST_FIELD = 'trip_cost'

    def __init__(self, algod_client, app_id=None):
        self.algod_client = algod_client
        self.teal_version = 5
        self.app_contract = CarSharingContract()
        self.app_id = app_id

    @property
    def escrow_bytes(self):
        if self.app_id is None:
            raise ValueError("App not deployed")

        escrow_fund_program_compiled = compileTeal(
            contract_escrow(app_id=self.app_id),
            mode=Mode.Signature,
            version=self.teal_version,
        )

        return algo_helper.compile_program(self.algod_client, escrow_fund_program_compiled)

    @property
    def escrow_address(self):
        return algo_logic.address(self.escrow_bytes)

    def create_trip(self, creator_pk, trip_creator_name, trip_start_address, trip_end_address,
                    trip_start_date, trip_end_date, trip_cost, trip_available_seats):
        """
        Create the Smart Contract dApp and start the trip
        :param creator_pk:
        :param trip_creator_name:
        :param trip_start_address:
        :param trip_end_address:
        :param trip_start_date:
        :param trip_end_date:
        :param trip_cost:
        :param trip_available_seats:
        :return:
        """
        # compile program to TEAL assembly
        approval_program_compiled = compileTeal(
            self.app_contract.approval_program(),
            mode=Mode.Application,
            version=self.teal_version,
        )

        clear_program_compiled = compileTeal(
            self.app_contract.clear_program(),
            mode=Mode.Application,
            version=self.teal_version
        )

        # compile program to binary
        approval_program_compiled = algo_helper.compile_program(self.algod_client, approval_program_compiled)
        clear_state_program_compiled = algo_helper.compile_program(self.algod_client, clear_program_compiled)

        app_args = [
            trip_creator_name,
            trip_start_address,
            trip_end_address,
            algo_helper.intToBytes(trip_start_date),
            algo_helper.intToBytes(trip_end_date),
            algo_helper.intToBytes(trip_cost),
            algo_helper.intToBytes(trip_available_seats),
        ]

        try:
            txn = ApplicationManager.create_app(self.algod_client,
                                                creator_pk,
                                                approval_program_compiled,
                                                clear_state_program_compiled,
                                                self.app_contract.global_schema,
                                                self.app_contract.local_schema,
                                                app_args)

            txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
            self.app_id = txn_response['application-index']
            utils.console_log("Application Created. New app-id: {}".format(self.app_id), "green")
        except Exception as e:
            utils.console_log("Error during create_app call: {}".format(e))
            return False

        return self.app_id

    def initialize_escrow(self, creator_pk):
        """
        Init an escrow contract
        :param creator_pk:
        :return:
        """
        try:
            app_args = [
                self.app_contract.AppMethods.initialize_escrow,
                decode_address(self.escrow_address),
            ]

            txn = ApplicationManager.call_app(algod_client=self.algod_client,
                                              private_key=creator_pk,
                                              app_id=self.app_id,
                                              app_args=app_args)
            ApplicationManager.send_transaction(self.algod_client, txn)
            utils.console_log("Application called.", "green")
        except Exception as e:
            utils.console_log("Error during initialize_escrow call: {}".format(e))
            return False

    def pay_escrow(self, user_private_key, amount):
        """
        Perform a payment to the escrow
        :param user_private_key:
        :param amount:
        """
        address = algo_helper.get_address_from_private_key(user_private_key)

        try:
            ApplicationManager.payment(self.algod_client,
                                       sender_address=address,
                                       receiver_address=self.escrow_address,
                                       amount=amount,
                                       sender_private_key=user_private_key)
        except Exception as e:
            utils.console_log("Error during pay_escrow call: {}".format(e))

    def refund_escrow(self, user_private_key, amount):
        """
        Perform a refund from the escrow
        :param user_private_key:
        :param amount:
        """
        address = algo_helper.get_address_from_private_key(user_private_key)

        try:
            ApplicationManager.payment(self.algod_client,
                                       sender_address=self.escrow_address,
                                       receiver_address=address,
                                       amount=amount,
                                       sender_private_key=user_private_key,
                                       sign_transaction=False)
        except Exception as e:
            utils.console_log("Error during pay_escrow call: {}".format(e))

    def participate(self, user_private_key, user_name):
        """
        Add an user to the trip
        :param user_private_key:
        :param user_name:
        """

        address = account.address_from_private_key(user_private_key)
        local_state = algo_helper.read_local_state(self.algod_client, address, self.app_id)
        if local_state is None:
            try:
                # opt in to write local state
                txn = ApplicationManager.opt_in_app(self.algod_client, user_private_key, self.app_id)
                txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
                utils.console_log("OptIn to app-id: {}".format(txn_response["txn"]["txn"]["apid"]), "green")
            except Exception as e:
                utils.console_log("Error during optin call: {}".format(e))

        try:
            global_state, creator_address = algo_helper.read_global_state(self.algod_client, self.app_id, False, False)
            cost = global_state.get('trip_cost')

            app_args = [
                self.app_contract.AppMethods.participate_trip,
                bytes(user_name, encoding="raw_unicode_escape")
            ]

            txn = ApplicationManager.call_app(algod_client=self.algod_client,
                                              private_key=user_private_key,
                                              app_id=self.app_id,
                                              app_args=app_args)

            escrow_address = str(Trip.escrow_address)
            payment_txn = ApplicationManager.payment(self.algod_client,
                                                     sender_address=address,
                                                     receiver_address=escrow_address,
                                                     amount=cost,
                                                     sender_private_key=user_private_key)

            ApplicationManager.send_group_transactions(self.algod_client, [txn, payment_txn])
        except Exception as e:
            utils.console_log("Error during participation call: {}".format(e))
            return False

        # read local state of application
        local_state = algo_helper.read_local_state(self.algod_client,
                                                   account.address_from_private_key(user_private_key),
                                                   self.app_id),

        # read global state of application
        global_state = algo_helper.read_global_state(self.algod_client, self.app_id)

    def cancel_participation(self, creator_private_key, user_private_key, user_name):
        """
        Cancel user participation to the trip
        :param creator_private_key:
        :param user_private_key:
        :param user_name:
        """

        address = account.address_from_private_key(user_private_key)
        local_state = algo_helper.read_local_state(self.algod_client, address, self.app_id)
        if local_state is None:
            try:
                # opt in to write local state
                txn = ApplicationManager.opt_in_app(self.algod_client, user_private_key, self.app_id)
                txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
                utils.console_log("OptIn to app-id: {}".format(txn_response["txn"]["txn"]["apid"]), "green")
            except Exception as e:
                utils.console_log("Error during optin call: {}".format(e))

        try:
            app_args = [
                self.app_contract.AppMethods.cancel_trip_participation,
                bytes(user_name, encoding="raw_unicode_escape")
            ]
            txn = ApplicationManager.call_app(
                algod_client=self.algod_client,
                private_key=user_private_key,
                app_id=self.app_id,
                app_args=app_args
            )

            global_state, creator_address = algo_helper.read_global_state(self.algod_client, self.app_id, False, False)
            cost = global_state.get('trip_cost')

            ApplicationManager.payment(self.algod_client,
                                       sender_address=creator_address,
                                       receiver_address=address,
                                       amount=cost,
                                       sender_private_key=creator_private_key)
        except Exception as e:
            utils.console_log("Error during participation cancel call: {}".format(e))
            return False

        # read local state of application
        local_state = algo_helper.read_local_state(self.algod_client,
                                                   account.address_from_private_key(user_private_key),
                                                   self.app_id),

        # read global state of application
        global_state = algo_helper.read_global_state(self.algod_client, self.app_id)

    def close_trip(self, creator_private_key, participating_users):
        """
        Close the trip and delete the Smart Contract dApp
        :param participating_users:
        :param creator_private_key:
        :return:
        """

        try:
            # delete application
            txn = ApplicationManager.delete_app(self.algod_client, creator_private_key, self.app_id)
            txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
            utils.console_log("Deleted Application with app-id: {}".format(txn_response["txn"]["txn"]["apid"]), "green")
        except Exception as e:
            utils.console_log("Error during delete_app call: {}".format(e))
            return False

        for test_user in participating_users:
            private_key = algo_helper.get_private_key_from_mnemonic(test_user.get('mnemonic'))
            address = algo_helper.get_address_from_private_key(private_key)
            local_state = algo_helper.read_local_state(self.algod_client, address, self.app_id)
            if local_state is not None:
                try:
                    # clear application from user account
                    txn = ApplicationManager.clear_app(self.algod_client, private_key, self.app_id)
                    txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
                    utils.console_log("Cleared app-id: {}".format(txn_response["txn"]["txn"]["apid"]), "green")
                except Exception as e:
                    utils.console_log("Error during clear_app call: {}".format(e))
                    return False
