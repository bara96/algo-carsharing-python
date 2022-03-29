import random

from algosdk import account
from algosdk.v2client import algod
from numpy.core.defchararray import strip

from constants import Constants
from helpers import algo_helper
from models.Trip import Trip
from utilities import utils


def read_state(algod_client, app_id, user_private_key=None):
    """
    Get the dApp global state / local state
    :param algod_client:
    :param app_id:
    :param user_private_key:
    """

    if app_id is None:
        utils.console_log("Invalid app_id")
        return False

    if user_private_key is not None:
        # read local state of application
        local_state = algo_helper.read_local_state(algod_client, account.address_from_private_key(user_private_key),
                                                   app_id),

    # read global state of application
    global_state = algo_helper.read_global_state(algod_client, app_id)

    app_info = algod_client.application_info(app_id)
    utils.console_log("Application Info:", 'blue')
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

    app_id = 37

    carsharing_trip = Trip(algod_client, app_id)

    color = 'blue'
    x = 1
    while x != 0:
        utils.console_log("--------------------------------------------", color)
        utils.console_log('What do you want to do?', color)
        utils.console_log('1) Create Trip', color)
        utils.console_log('2) Participate', color)
        utils.console_log('3) Cancel Participation', color)
        utils.console_log('4) Delete Trip', color)
        utils.console_log('5) Get Trip State', color)
        utils.console_log("--------------------------------------------", color)
        x = int(strip(input()))
        if x == 1:
            trip_creator_name = "Matteo Baratella"
            trip_start_add = "Mestre"
            trip_end_add = "Milano"
            trip_start_date = algo_helper.datetime_to_rounds(algod_client, "2022-04-10 15:00")
            trip_end_date = algo_helper.datetime_to_rounds(algod_client, "2022-04-10 21:00")
            trip_cost = 5000
            trip_available_seats = 4

            app_id = carsharing_trip.create_trip(creator_private_key, trip_creator_name, trip_start_add, trip_end_add, trip_start_date, trip_end_date, trip_cost, trip_available_seats)
            carsharing_trip.initialize_escrow(creator_private_key)
        elif x == 2:
            if app_id is None:
                utils.console_log("Invalid app_id")
                continue
            test_user = get_test_user(Constants.accounts, True)
            test_user_pk = algo_helper.get_private_key_from_mnemonic(test_user.get('mnemonic'))
            carsharing_trip.participate(test_user_pk, test_user.get('name'))
        elif x == 3:
            if app_id is None:
                utils.console_log("Invalid app_id")
            test_user = get_test_user(Constants.accounts, True)
            test_user_pk = algo_helper.get_private_key_from_mnemonic(test_user.get('mnemonic'))
            carsharing_trip.cancel_participation(creator_private_key, test_user_pk, test_user.get('name'))
        elif x == 4:
            if app_id is None:
                utils.console_log("Invalid app_id")
                continue
            carsharing_trip.close_trip(creator_private_key, Constants.accounts)
        elif x == 5:
            read_state(algod_client, app_id)
        else:
            print("Exiting..")


if __name__ == "__main__":
    main()
