from algosdk import account, transaction
from algosdk import logic as algo_logic
from algosdk.encoding import decode_address
from algosdk.v2client import algod
from pyteal import compileTeal, Mode

from constants import get_env
from helpers import algo_helper
from models.ApplicationManager import ApplicationManager
from smart_contracts.contract_carsharing import CarSharingContract
from smart_contracts.contract_escrow import contract_escrow
from utilities import utils


class Trip:
    def __init__(self,
                 algod_client: algod.AlgodClient,
                 app_id: int = None):
        self.algod_client = algod_client
        self.teal_version = 5
        self.app_contract = CarSharingContract()
        self.app_id = app_id

        # read contract program from env
        if get_env('APPROVAL_PROGRAM') is not None and get_env('CLEAR_STATE_PROGRAM') is not None:
            self.approval_program_hash = get_env('APPROVAL_PROGRAM')
            self.clear_state_program_hash = get_env('CLEAR_STATE_PROGRAM')
        else:
            self.approval_program_hash = None
            self.clear_state_program_hash = None

    @property
    def escrow_bytes(self):
        """
        Get escrow contract compiled program
        :return:
        """
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
        """
        Return the escrow address
        :return:
        """
        return algo_logic.address(self.escrow_bytes)

    def create_app(self,
                   creator_private_key: str,
                   trip_creator_name: str,
                   trip_start_address: str,
                   trip_end_address: str,
                   trip_start_date: int,
                   trip_end_date: int,
                   trip_cost: int,
                   trip_available_seats: int):
        """
        Create the Smart Contract dApp and start the trip
        :param creator_private_key:
        :param trip_creator_name:
        :param trip_start_address:
        :param trip_end_address:
        :param trip_start_date: round for the start date
        :param trip_end_date: round for the end date
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

        address = algo_helper.get_address_from_private_key(creator_private_key)
        try:
            txn = ApplicationManager.create_app(algod_client=self.algod_client,
                                                address=address,
                                                approval_program=approval_program_compiled,
                                                clear_program=clear_state_program_compiled,
                                                global_schema=self.app_contract.global_schema,
                                                local_schema=self.app_contract.local_schema,
                                                app_args=app_args,
                                                sign_transaction=creator_private_key)

            txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
            self.app_id = txn_response['application-index']
            utils.console_log("Application Created. New app-id: {}".format(self.app_id), "green")
        except Exception as e:
            utils.console_log("Error during create_app call: {}".format(e))
            return False

        return self.app_id

    def update_app(self, creator_private_key: str):
        """
        Create the Smart Contract dApp and start the trip
        :param creator_private_key:
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

        address = algo_helper.get_address_from_private_key(creator_private_key)
        try:
            txn = ApplicationManager.update_app(algod_client=self.algod_client,
                                                address=address,
                                                approval_program=approval_program_compiled,
                                                clear_program=clear_state_program_compiled,
                                                global_schema=self.app_contract.global_schema,
                                                local_schema=self.app_contract.local_schema,
                                                app_args=None,
                                                sign_transaction=creator_private_key)

            txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
            utils.console_log("Updated Application with app-id: {}".format(self.app_id), "green")
        except Exception as e:
            utils.console_log("Error during create_app call: {}".format(e))
            return False

        return self.app_id

    def update_trip_info(self,
                         creator_private_key: str,
                         trip_creator_name: str,
                         trip_start_address: str,
                         trip_end_address: str,
                         trip_start_date: int,
                         trip_end_date: int,
                         trip_cost: int,
                         trip_available_seats: int):
        """
        Create the Smart Contract dApp and start the trip
        :param creator_private_key:
        :param trip_creator_name:
        :param trip_start_address:
        :param trip_end_address:
        :param trip_start_date: round for the start date
        :param trip_end_date: round for the end date
        :param trip_cost:
        :param trip_available_seats:
        :return:
        """
        app_args = [
            self.app_contract.AppMethods.update_trip,
            trip_creator_name,
            trip_start_address,
            trip_end_address,
            algo_helper.intToBytes(trip_start_date),
            algo_helper.intToBytes(trip_end_date),
            algo_helper.intToBytes(trip_cost),
            algo_helper.intToBytes(trip_available_seats),
        ]

        address = algo_helper.get_address_from_private_key(creator_private_key)
        try:
            txn = ApplicationManager.call_app(algod_client=self.algod_client,
                                              address=address,
                                              app_id=self.app_id,
                                              app_args=app_args,
                                              sign_transaction=creator_private_key)

            txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
            utils.console_log("Updated Info for Application with app-id: {}".format(self.app_id), "green")
        except Exception as e:
            utils.console_log("Error during update_trip_info call: {}".format(e))
            return False

        return self.app_id

    def initialize_escrow(self, creator_private_key: str):
        """
        Init an escrow contract
        :param creator_private_key:
        :return:
        """
        app_args = [
            self.app_contract.AppMethods.initialize_escrow,
            decode_address(self.escrow_address)
        ]

        try:
            address = algo_helper.get_address_from_private_key(creator_private_key)
            txn = ApplicationManager.call_app(algod_client=self.algod_client,
                                              address=address,
                                              app_id=self.app_id,
                                              app_args=app_args,
                                              sign_transaction=creator_private_key)

            txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
            utils.console_log("Escrow initialized for Application with app-id {} with address: {}"
                              .format(self.app_id, self.escrow_address), "green")
        except Exception as e:
            utils.console_log("Error during initialize_escrow call: {}".format(e))
            return False

    def fund_escrow(self, creator_private_key: str):
        """
        Fund the escrow contract
        :param creator_private_key:
        :return:
        """
        address = account.address_from_private_key(creator_private_key)

        try:
            global_state, creator_address, _, _ = algo_helper.read_global_state(self.algod_client, self.app_id, False,
                                                                                False)
            escrow_address = algo_helper.BytesToAddress(global_state.get("escrow_address"))

            txn = ApplicationManager.payment(algod_client=self.algod_client,
                                             sender_address=address,
                                             receiver_address=escrow_address,
                                             amount=ApplicationManager.Variables.escrow_min_balance,
                                             sign_transaction=creator_private_key)

            txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
            utils.console_log("Escrow funded with address: {}".format(escrow_address), "green")
        except Exception as e:
            utils.console_log("Error during fund_escrow: {}".format(e))
            return False

    def participate(self, user_private_key: str, user_name: str):
        """
        Add a user to the trip
        Perform a payment transaction from the user to the escrow
        Perform a check transaction from the verifier
        :param user_private_key:
        :param user_name:
        """

        address = account.address_from_private_key(user_private_key)
        local_state = algo_helper.read_local_state(self.algod_client, address, self.app_id)
        if local_state is None:
            try:
                # opt in to write local state
                call_txn = ApplicationManager.opt_in_app(algod_client=self.algod_client,
                                                         address=address,
                                                         app_id=self.app_id,
                                                         sign_transaction=user_private_key)
                txn_response = ApplicationManager.send_transaction(self.algod_client, call_txn)
                utils.console_log("OptIn to Application with app-id: {}"
                                  .format(self.app_id), "green")
            except Exception as e:
                utils.console_log("Error during optin call: {}".format(e))

        app_args = [
            self.app_contract.AppMethods.participate_trip,
            bytes(user_name, encoding="raw_unicode_escape")
        ]
        try:
            global_state, \
            creator_address, \
            approval_program, \
            clear_state_program = algo_helper.read_global_state(client=self.algod_client,
                                                                app_id=self.app_id,
                                                                to_array=False,
                                                                show=False)

            self.check_program_hash(approval_program=approval_program, clear_state_program=clear_state_program)

            trip_cost = global_state.get("trip_cost")
            escrow_address = algo_helper.BytesToAddress(global_state.get("escrow_address"))

            call_txn = ApplicationManager.call_app(algod_client=self.algod_client,
                                                   address=address,
                                                   app_id=self.app_id,
                                                   app_args=app_args)

            payment_txn = ApplicationManager.payment(algod_client=self.algod_client,
                                                     sender_address=address,
                                                     receiver_address=escrow_address,
                                                     amount=trip_cost)
            # Atomic transfer
            gid = transaction.calculate_group_id([call_txn, payment_txn])
            call_txn.group = gid
            payment_txn.group = gid

            call_txn = call_txn.sign(user_private_key)
            payment_txn = payment_txn.sign(user_private_key)

            txn_response = ApplicationManager.send_group_transactions(self.algod_client, [call_txn, payment_txn])
            utils.console_log("Participated to Application with app-id: {}"
                              .format(self.app_id), "green")
        except Exception as e:
            utils.console_log("Error during participation call: {}".format(e))
            return False

    def cancel_participation(self,
                             creator_private_key: str,
                             user_private_key: str,
                             user_name: str):
        """
        Cancel user participation to the trip
        Perform a payment refund transaction from the escrow to the user
        Perform a check transaction from the verifier
        :param creator_private_key:
        :param user_private_key:
        :param user_name:
        """

        address = account.address_from_private_key(user_private_key)
        local_state = algo_helper.read_local_state(self.algod_client, address, self.app_id)
        if local_state is None:
            try:
                # opt in to write local state
                txn = ApplicationManager.opt_in_app(algod_client=self.algod_client,
                                                    address=address,
                                                    app_id=self.app_id,
                                                    sign_transaction=user_private_key)
                txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
                utils.console_log("OptIn to Application with app-id: {}"
                                  .format(self.app_id), "green")
            except Exception as e:
                utils.console_log("Error during optin call: {}".format(e))

        app_args = [
            bytes(self.app_contract.AppMethods.cancel_trip_participation, encoding="raw_unicode_escape"),
            bytes(user_name, encoding="raw_unicode_escape")
        ]

        try:
            global_state, \
            creator_address, \
            approval_program, \
            clear_state_program = algo_helper.read_global_state(client=self.algod_client,
                                                                app_id=self.app_id,
                                                                to_array=False,
                                                                show=False)

            self.check_program_hash(approval_program=approval_program, clear_state_program=clear_state_program)

            trip_cost = global_state.get("trip_cost")
            escrow_address = algo_helper.BytesToAddress(global_state.get("escrow_address"))

            call_txn = ApplicationManager.call_app(algod_client=self.algod_client,
                                                   address=address,
                                                   app_id=self.app_id,
                                                   app_args=app_args)

            payment_txn = ApplicationManager.payment(algod_client=self.algod_client,
                                                     sender_address=escrow_address,
                                                     receiver_address=address,
                                                     amount=trip_cost)
            # Atomic transfer
            gid = transaction.calculate_group_id([call_txn, payment_txn])
            call_txn.group = gid
            payment_txn.group = gid

            call_txn = call_txn.sign(user_private_key)
            escrow_logic_signature = transaction.LogicSig(self.escrow_bytes)
            payment_txn = transaction.LogicSigTransaction(payment_txn, escrow_logic_signature)

            txn_response = ApplicationManager.send_group_transactions(self.algod_client, [call_txn, payment_txn])
            utils.console_log("Participation canceled to Application with app-id: {}"
                              .format(self.app_id), "green")
        except Exception as e:
            utils.console_log("Error during participation cancel call: {}".format(e))
            return False

    def start_trip(self, creator_private_key: str):
        """
        Start a trip and transfer founding to the creator
        Perform a payment refund transaction from the escrow to the creator
        Perform a check transaction from the verifier
        :param creator_private_key:
        """

        address = account.address_from_private_key(creator_private_key)

        app_args = [
            bytes(self.app_contract.AppMethods.start_trip, encoding="raw_unicode_escape"),
        ]

        try:
            global_state, \
            creator_address, \
            approval_program, \
            clear_state_program = algo_helper.read_global_state(client=self.algod_client,
                                                                app_id=self.app_id,
                                                                to_array=False,
                                                                show=False)

            self.check_program_hash(approval_program=approval_program, clear_state_program=clear_state_program)

            trip_cost = global_state.get("trip_cost")
            escrow_address = algo_helper.BytesToAddress(global_state.get("escrow_address"))

            call_txn = ApplicationManager.call_app(algod_client=self.algod_client,
                                                   address=address,
                                                   app_id=self.app_id,
                                                   app_args=app_args)

            payment_txn = ApplicationManager.payment(algod_client=self.algod_client,
                                                     sender_address=escrow_address,
                                                     receiver_address=address,
                                                     amount=trip_cost,
                                                     close_remainder_to=address)
            # Atomic transfer
            gid = transaction.calculate_group_id([call_txn, payment_txn])
            call_txn.group = gid
            payment_txn.group = gid

            call_txn = call_txn.sign(creator_private_key)
            escrow_logic_signature = transaction.LogicSig(self.escrow_bytes)
            payment_txn = transaction.LogicSigTransaction(payment_txn, escrow_logic_signature)

            ApplicationManager.send_group_transactions(self.algod_client, [call_txn, payment_txn])
        except Exception as e:
            utils.console_log("Error during start_trip call: {}".format(e))
            return False

    def close_trip(self, creator_private_key: str, participating_users: [dict]):
        """
        Close the trip and delete the Smart Contract dApp
        :param participating_users:
        :param creator_private_key:
        :return:
        """

        try:
            # delete application
            address = algo_helper.get_address_from_private_key(creator_private_key)
            txn = ApplicationManager.delete_app(algod_client=self.algod_client,
                                                address=address,
                                                app_id=self.app_id,
                                                sign_transaction=creator_private_key)
            txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
            utils.console_log("Deleted Application with app-id: {}".format(self.app_id), "green")
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
                    txn = ApplicationManager.clear_app(algod_client=self.algod_client,
                                                       address=address,
                                                       app_id=self.app_id,
                                                       sign_transaction=private_key)
                    txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
                    utils.console_log("Cleared app-id: {}".format(self.app_id), "green")
                except Exception as e:
                    utils.console_log("Error during clear_app call: {}".format(e))
                    return False

    def check_program_hash(self, approval_program, clear_state_program):
        """
        Check the contract programs
        @param approval_program: given approval program hash
        @param clear_state_program: given clear state program hash
        """
        if self.approval_program_hash is not None and self.clear_state_program_hash is not None:
            if approval_program != self.approval_program_hash:
                print("Given hash:")
                print(approval_program)
                print("Expected hash:")
                print(self.approval_program_hash)
                raise Exception("Approval program hash is invalid")
            if clear_state_program != self.clear_state_program_hash:
                print("Given hash:")
                print(clear_state_program)
                print("Expected hash:")
                print(self.clear_state_program_hash)
                raise Exception("Clear state program hash is invalid")
