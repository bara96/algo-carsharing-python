import random

from algosdk import account
from algosdk.future import transaction
from numpy.core.defchararray import strip
from pyteal import compileTeal, Mode

import constants
from contract_carsharing import approval_program, clear_state_program
from helpers import algo_helper
from models.ApplicationManager import ApplicationManager
from utilities import utils


def read_state(applicationHelper, app_id, user_private_key=None):
    """
    Get the dApp global state / local state
    :param applicationHelper:
    :param app_id:
    :param user_private_key:
    """
    algod_client = applicationHelper.get_algod_client()

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


def cancel_participation(applicationHelper, app_id, user_private_key, user_name):
    """
    Cancel user participation to the trip
    :param applicationHelper:
    :param app_id:
    :param user_private_key:
    :param user_name:
    """
    algod_client = applicationHelper.get_algod_client()

    try:
        global_state = algo_helper.read_global_state(algod_client, app_id, False, False)
        app_args = [b"Cancel", bytes(user_name, encoding="raw_unicode_escape")]
        applicationHelper.call_app(user_private_key, app_id, app_args)
    except Exception as e:
        utils.console_log("Error during participation cancel call: {}".format(e))
        return False

    # read local state of application
    local_state = algo_helper.read_local_state(algod_client, account.address_from_private_key(user_private_key),
                                               app_id),

    # read global state of application
    global_state = algo_helper.read_global_state(algod_client, app_id)


def participate(applicationHelper, app_id, user_private_key, user_name):
    """
    Add an user to the trip
    :param applicationHelper:
    :param app_id:
    :param user_private_key:
    :param user_name:
    """
    algod_client = applicationHelper.get_algod_client()

    address = account.address_from_private_key(user_private_key)
    local_state = algo_helper.read_local_state(algod_client, address, app_id)
    if local_state is None:
        try:
            # opt in to write local state
            applicationHelper.opt_in_app(user_private_key, app_id)
        except Exception as e:
            utils.console_log("Error during optin call: {}".format(e))

    try:
        global_state = algo_helper.read_global_state(algod_client, app_id, False, False)
        app_args = [b"Participate", bytes(user_name, encoding="raw_unicode_escape")]
        applicationHelper.call_app(user_private_key, app_id, app_args)
    except Exception as e:
        utils.console_log("Error during participation call: {}".format(e))
        return False

    # read local state of application
    local_state = algo_helper.read_local_state(algod_client, account.address_from_private_key(user_private_key),
                                               app_id),

    # read global state of application
    global_state = algo_helper.read_global_state(algod_client, app_id)


def create_trip(applicationHelper, creator_private_key):
    """
    Create the Smart Contract dApp and start the trip
    :param applicationHelper:
    :param creator_private_key:
    :return:
    """
    algod_client = applicationHelper.get_algod_client()

    # get PyTeal approval program
    approval_program_ast = approval_program()
    # compile program to TEAL assembly
    approval_program_teal = compileTeal(approval_program_ast, mode=Mode.Application, version=5)
    # compile program to binary
    approval_program_compiled = algo_helper.compile_program(algod_client, approval_program_teal)

    # get PyTeal clear state program
    clear_state_program_ast = clear_state_program()
    # compile program to TEAL assembly
    clear_state_program_teal = compileTeal(clear_state_program_ast, mode=Mode.Application, version=5)
    # compile program to binary
    clear_state_program_compiled = algo_helper.compile_program(algod_client, clear_state_program_teal)

    tripCreatorName = "Matteo Baratella"
    tripStartAdd = "Mestre"
    tripEndAdd = "Milano"
    tripStartDate = algo_helper.datetime_to_rounds(algod_client, "2022-04-10 15:00")
    tripEndDate = algo_helper.datetime_to_rounds(algod_client, "2022-04-10 21:00")
    tripCost = 1000
    tripAvailableSeats = 4

    # declare application state storage (immutable)
    local_ints = 1  # for participating
    local_bytes = 0
    global_ints = 4  # 4 for setup
    global_bytes = 5  # 4 for setup + 1 for participants
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    # create list of bytes for app args
    app_args = [
        tripCreatorName,
        tripStartAdd,
        tripEndAdd,
        algo_helper.intToBytes(tripStartDate),
        algo_helper.intToBytes(tripEndDate),
        algo_helper.intToBytes(tripCost),
        algo_helper.intToBytes(tripAvailableSeats),
    ]

    try:
        app_id = applicationHelper.create_app(creator_private_key, approval_program_compiled,
                                           clear_state_program_compiled,
                                           global_schema, local_schema, app_args)
    except Exception as e:
        utils.console_log("Error during create_app call: {}".format(e))
        return False

    return app_id


def close_trip(applicationHelper, app_id, creator_private_key, participating_users):
    """
    Close the trip and delete the Smart Contract dApp
    :param applicationHelper:
    :param app_id:
    :param creator_private_key:
    :param participating_users:
    :return:
    """
    algod_client = applicationHelper.get_algod_client()
    try:
        # delete application
        applicationHelper.delete_app(creator_private_key, app_id)
    except Exception as e:
        utils.console_log("Error during delete_app call: {}".format(e))
        return False

    for test_user in participating_users:
        address = account.address_from_private_key(test_user.get('private_key'))
        local_state = algo_helper.read_local_state(algod_client, address, app_id)
        if local_state is not None:
            try:
                # clear application from user account
                applicationHelper.clear_app(test_user.get('private_key'), app_id)
            except Exception as e:
                utils.console_log("Error during clear_app call: {}".format(e))
                return False


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
    # initialize an application manager with algod client
    applicationManager = ApplicationManager(algod_token=constants.algod_token,
                                            algod_address=constants.algod_address,
                                            transaction_note=constants.transaction_note)

    # define private keys
    creator_private_key = algo_helper.get_private_key_from_mnemonic(constants.creator_mnemonic)

    app_id = None
    if constants.app_id_global is not None:
        app_id = constants.app_id_global

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
            app_id = create_trip(applicationManager, creator_private_key)
        elif x == 2:
            if app_id is None:
                utils.console_log("Invalid app_id")
                continue
            test_user = get_test_user(constants.accounts, True)
            test_user_pk = algo_helper.get_private_key_from_mnemonic(test_user.get('mnemonic'))
            participate(applicationManager, app_id, test_user_pk, test_user.get('name'))
        elif x == 3:
            if app_id is None:
                utils.console_log("Invalid app_id")
            test_user = get_test_user(constants.accounts, True)
            test_user_pk = algo_helper.get_private_key_from_mnemonic(test_user.get('mnemonic'))
            cancel_participation(applicationManager, app_id, test_user_pk, test_user.get('name'))
        elif x == 4:
            if app_id is None:
                utils.console_log("Invalid app_id")
                continue
            close_trip(applicationManager, app_id, creator_private_key, constants.accounts)
        elif x == 5:
            read_state(applicationManager, app_id)
        else:
            print("Exiting..")


if __name__ == "__main__":
    main()
