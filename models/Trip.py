from algosdk import account
from pyteal import compileTeal, Mode

from smart_contracts.contract_carsharing import CarSharingContractASC1
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
        self.app_contract = CarSharingContractASC1()
        self.app_id = app_id

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
            self.app_id = ApplicationManager.create_app(self.algod_client,
                                                        creator_pk,
                                                        approval_program_compiled,
                                                        clear_state_program_compiled,
                                                        self.app_contract.global_schema,
                                                        self.app_contract.local_schema,
                                                        app_args)
        except Exception as e:
            utils.console_log("Error during create_app call: {}".format(e))
            return False

        return self.app_id

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
                ApplicationManager.opt_in_app(self.algod_client, user_private_key, self.app_id)
            except Exception as e:
                utils.console_log("Error during optin call: {}".format(e))

        try:
            global_state = algo_helper.read_global_state(self.algod_client, self.app_id, False, False)
            app_args = [b"participateTrip", bytes(user_name, encoding="raw_unicode_escape")]
            ApplicationManager.call_app(self.algod_client, user_private_key, self.app_id, app_args)
        except Exception as e:
            utils.console_log("Error during participation call: {}".format(e))
            return False

        # read local state of application
        local_state = algo_helper.read_local_state(self.algod_client,
                                                   account.address_from_private_key(user_private_key),
                                                   self.app_id),

        # read global state of application
        global_state = algo_helper.read_global_state(self.algod_client, self.app_id)

    def cancel_participation(self, user_private_key, user_name):
        """
        Cancel user participation to the trip
        :param user_private_key:
        :param user_name:
        """

        try:
            global_state = algo_helper.read_global_state(self.algod_client, self.app_id, False, False)
            app_args = [b"cancelParticipation", bytes(user_name, encoding="raw_unicode_escape")]
            ApplicationManager.call_app(self.algod_client, user_private_key, self.app_id, app_args)
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
            ApplicationManager.delete_app(self.algod_client, creator_private_key, self.app_id)
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
                    ApplicationManager.clear_app(self.algod_client, private_key, self.app_id)
                except Exception as e:
                    utils.console_log("Error during clear_app call: {}".format(e))
                    return False
