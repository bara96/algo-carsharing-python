import random

from algosdk import account
from algosdk.v2client import algod
from numpy.core.defchararray import strip

from constants import Constants, get_env
from helpers import algo_helper
from models.Trip import Trip
from utilities import utils


def read_state(algod_client, app_id, user_private_key=None, show_debug=False):
    """
    Get the dApp global state / local state
    :param algod_client:
    :param app_id:
    :param user_private_key:
    :param show_debug:
    """

    if app_id is None:
        utils.console_log("Invalid app_id")
        return False

    if user_private_key is not None:
        # read local state of application
        local_state = algo_helper.read_local_state(algod_client,
                                                   account.address_from_private_key(user_private_key),
                                                   app_id),

    # read global state of application
    global_state, creator, approval_program, clear_state_program = algo_helper.read_global_state(client=algod_client,
                                                                                                 app_id=app_id,
                                                                                                 to_array=False,
                                                                                                 show=False)
    escrow_address = algo_helper.BytesToAddress(global_state.get('escrow_address'))

    utils.console_log("App id: {}".format(app_id), 'blue')
    utils.console_log("Global State:", 'blue')
    print(utils.toArray(global_state))
    utils.console_log("Approval Program:", 'blue')
    print(approval_program)
    utils.console_log("Clear State Program:", 'blue')
    print(clear_state_program)
    utils.console_log("Creator Address:", 'blue')
    print(creator)
    utils.console_log("Escrow Address:", 'blue')
    print(escrow_address)
    utils.console_log("Escrow Info:", 'blue')
    print(algod_client.account_info(escrow_address))

    if show_debug:
        utils.console_log("Application Info:", 'blue')
        app_info = algod_client.application_info(app_id)
        utils.parse_response(app_info)


def get_test_user(user_list, ask_selection=True):
    """
    Select a test user account from given user list
    :param user_list:
    :param ask_selection: if True, ask user for selection, otherwise select the user randomly
    """
    if ask_selection:
        print('With which user?')
        for i in range(0, len(user_list)):
            print('{}) {}'.format(i, user_list[i].get('name')))
        y = int(strip(input()))
        if y <= 0 or y > len(user_list):
            y = 0
    else:
        y = random.randint(0, len(user_list) - 1)

    return user_list[y]


def main():
    # define private keys
    creator_private_key = algo_helper.get_private_key_from_mnemonic(Constants.creator_mnemonic)
    algod_client = algod.AlgodClient(Constants.algod_token, Constants.algod_address)

    app_id = int(get_env('APP_ID'))
    accounts = Constants.accounts

    carsharing_trip = Trip(algod_client=algod_client, app_id=app_id)
    # ------- trip info ---------
    trip_creator_name = "Matteo Baratella"
    trip_start_add = "Mestre"
    trip_end_add = "Milano"
    trip_start_date = algo_helper.datetime_to_rounds(algod_client, "2022-04-10 15:00")
    trip_end_date = algo_helper.datetime_to_rounds(algod_client, "2022-04-10 21:00")
    trip_cost = 5000
    trip_seats = 4
    # ---------------------------

    color = 'blue'
    x = 1
    while x != 0:
        utils.console_log("--------------------------------------------", color)
        utils.console_log('What do you want to do?', color)
        utils.console_log('1) Create Trip', color)
        utils.console_log('2) Participate', color)
        utils.console_log('3) Cancel Participation', color)
        utils.console_log('4) Start Trip', color)
        utils.console_log('5) Update Trip', color)
        utils.console_log('6) Delete Trip', color)
        utils.console_log('7) Get Trip State', color)
        utils.console_log("--------------------------------------------", color)
        x = int(strip(input()))
        if x == 1:
            carsharing_trip.create_app(creator_private_key=creator_private_key,
                                       trip_creator_name=trip_creator_name,
                                       trip_start_address=trip_start_add,
                                       trip_end_address=trip_end_add,
                                       trip_start_date=trip_start_date,
                                       trip_end_date=trip_end_date,
                                       trip_cost=trip_cost,
                                       trip_available_seats=trip_seats)
            carsharing_trip.initialize_escrow(creator_private_key)
            carsharing_trip.fund_escrow(creator_private_key)
        elif x == 2:
            if carsharing_trip.app_id is None:
                utils.console_log("Invalid app_id")
                continue
            test_user = get_test_user(accounts, True)
            test_user_pk = algo_helper.get_private_key_from_mnemonic(test_user.get('mnemonic'))
            carsharing_trip.participate(test_user_pk, test_user.get('name'))
        elif x == 3:
            if carsharing_trip.app_id is None:
                utils.console_log("Invalid app_id")

            test_user = get_test_user(accounts, True)
            test_user_pk = algo_helper.get_private_key_from_mnemonic(test_user.get('mnemonic'))
            carsharing_trip.cancel_participation(creator_private_key, test_user_pk, test_user.get('name'))
        elif x == 4:
            if carsharing_trip.app_id is None:
                utils.console_log("Invalid app_id")
                continue
            carsharing_trip.start_trip(creator_private_key)
        elif x == 5:
            if carsharing_trip.app_id is None:
                utils.console_log("Invalid app_id")
                continue
            carsharing_trip.update_trip_info(creator_private_key=creator_private_key,
                                             trip_creator_name=trip_creator_name,
                                             trip_start_address=trip_start_add,
                                             trip_end_address=trip_end_add,
                                             trip_start_date=trip_start_date,
                                             trip_end_date=trip_end_date,
                                             trip_cost=trip_cost,
                                             trip_available_seats=trip_seats)
        elif x == 6:
            utils.console_log("Are you sure?", 'red')
            y = strip(input())
            if y != "y" and y != "yes":
                continue
            if carsharing_trip.app_id is None:
                utils.console_log("Invalid app_id")
            carsharing_trip.close_trip(creator_private_key, accounts)
        elif x == 7:
            read_state(algod_client, carsharing_trip.app_id, show_debug=False)
        else:
            print("Exiting..")


if __name__ == "__main__":
    main()
