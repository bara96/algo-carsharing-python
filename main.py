import random
import numpy as np

from algosdk import account
from algosdk.future import transaction
from algosdk.v2client import algod
from pyteal import compileTeal, Mode

from contract_carsharing import approval_program, clear_state_program
from helpers import contract_helper, application_helper
from utils import account_utils, misc_utils

# creator user declared account mnemonics
creator_mnemonic = 'armed note crew promote scheme luxury impulse genius manage mutual cash local imitate flight zero attend expose device amazing guilt clap leader snow abandon artefact'

# array of pre-generated and funded users
generated_test_users = np.array(
    [
        {'name': 'User1', 'private_key': '5Xi+rZAPUvK1nFYDjWWn/H7Zxlsjm8Do8XK9kjAk/IPtEquYsn7a1cIWwB0W/ihucolAoY1KtBrFD2xe7v/+HA=='},
        {'name': 'User2', 'private_key': 'CyHrncs+Fn+oZXhL/RRehK+Cr9WuWf6HuHaY7UkJlNL/ikqUVLXBbBmEZlG8pYGL0SJ/lB0Irykd4Fh/y+/BEA=='},
        {'name': 'User3', 'private_key':'HqzLENGS8QCRQFhtoRVbhipeha/8AJTxLDn30Yvv/MfchaTQk35PRmVRJni6xFhhkrAtoPw5P0t92BQbQiuMbQ=='},
    ])

# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# app id, to reuse an old app
app_id_global = 76500516


def read_state(algod_client, app_id, user_private_key=None):
    """
    Get the dApp global state / local state
    :param algod_client:
    :param app_id:
    :param user_private_key:
    """
    if user_private_key is not None:
        # read local state of application
        local_state = contract_helper.read_local_state(algod_client, account.address_from_private_key(user_private_key),
                                                       app_id),
        misc_utils.console_log("Local state: {}".format(local_state), 'blue')

    # read global state of application
    global_state = contract_helper.read_global_state(algod_client, app_id)
    misc_utils.console_log("Global state: {}".format(global_state), 'blue')


def cancel_participation(algod_client, app_id, user_private_key, user_name):
    """
    Cancel user participation to the dApp
    :param algod_client:
    :param app_id:
    :param user_private_key:
    :param user_name:
    """
    try:
        app_args = [b"Cancel", bytes(user_name, encoding="raw_unicode_escape")]
        application_helper.call_app(algod_client, user_private_key, app_id, app_args)
    except Exception as e:
        misc_utils.console_log("Error during participation cancel call: {}".format(e))
        return False

    # read local state of application
    local_state = contract_helper.read_local_state(algod_client, account.address_from_private_key(user_private_key),
                                                   app_id),
    misc_utils.console_log("Local state: {}".format(local_state), 'blue')

    # read global state of application
    global_state = contract_helper.read_global_state(algod_client, app_id)
    misc_utils.console_log("Global state: {}".format(global_state), 'blue')


def participate(algod_client, app_id, user_private_key, user_name):
    """
    Join a user to the dApp
    :param algod_client:
    :param app_id:
    :param user_private_key:
    :param user_name:
    """
    try:
        # opt in to write local state
        application_helper.opt_in_app(algod_client, user_private_key, app_id)
    except Exception as e:
        misc_utils.console_log("Error during optin call: {}".format(e))

    try:
        app_args = [b"Participate", bytes(user_name, encoding="raw_unicode_escape")]
        application_helper.call_app(algod_client, user_private_key, app_id, app_args)
    except Exception as e:
        misc_utils.console_log("Error during participation call: {}".format(e))
        return False

    # read local state of application
    local_state = contract_helper.read_local_state(algod_client, account.address_from_private_key(user_private_key),
                                                   app_id),
    misc_utils.console_log("Local state: {}".format(local_state), 'blue')

    # read global state of application
    global_state = contract_helper.read_global_state(algod_client, app_id)
    misc_utils.console_log("Global state: {}".format(global_state), 'blue')


def create_trip(algod_client, creator_private_key):
    """
    Create the Smart Contract dApp
    :param algod_client:
    :param creator_private_key:
    :return:
    """
    # get PyTeal approval program
    approval_program_ast = approval_program()
    # compile program to TEAL assembly
    approval_program_teal = compileTeal(approval_program_ast, mode=Mode.Application, version=5)
    # compile program to binary
    approval_program_compiled = contract_helper.compile_program(algod_client, approval_program_teal)

    # get PyTeal clear state program
    clear_state_program_ast = clear_state_program()
    # compile program to TEAL assembly
    clear_state_program_teal = compileTeal(clear_state_program_ast, mode=Mode.Application, version=5)
    # compile program to binary
    clear_state_program_compiled = contract_helper.compile_program(algod_client, clear_state_program_teal)

    tripCreatorName = "Matteo Baratella"
    tripStartAdd = "Mestre"
    tripEndAdd = "Milano"
    tripStartDate = "2022-03-20 12:00"
    tripEndDate = "2022-03-20 15:00"
    tripCost = 1000
    tripAvailableSeats = 4

    # declare application state storage (immutable)
    local_ints = 1
    local_bytes = 1
    global_ints = 2 + tripAvailableSeats
    global_bytes = (6 + 4)  # 6 for setup, 4 for participants
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    # create list of bytes for app args
    app_args = [
        tripCreatorName,
        tripStartAdd,
        tripEndAdd,
        tripStartDate,
        tripEndDate,
        contract_helper.intToBytes(tripCost),
        contract_helper.intToBytes(tripAvailableSeats),
    ]

    app_id = application_helper.create_app(algod_client, creator_private_key, approval_program_compiled,
                                           clear_state_program_compiled,
                                           global_schema, local_schema, app_args)
    return app_id


def close_trip(algod_client, app_id, creator_private_key, participating_users):
    try:
        # delete application
        application_helper.delete_app(algod_client, creator_private_key, app_id)
    except Exception as e:
        misc_utils.console_log("Error during delete_app call: {}".format(e))
        return False

    for test_user in participating_users:
        try:
            # clear application from user account
            application_helper.clear_app(algod_client, test_user.get('private_key'), app_id)
        except Exception as e:
            misc_utils.console_log("Error during clear_app call: {}".format(e))
            return False


def get_test_user(user_list, ask_selection=True):
    """
    Select a user account from given user array
    :param user_list:
    :param ask_selection: if True, ask user for selection, otherwise select the user randomly
    """
    if ask_selection:
        print('With which user?')
        for i in range(0, len(user_list)):
            print('{}) {}'.format(i, user_list[i].get('name')))
        y = int(input())
        if y <= 0 or y > len(user_list):
            y = 0
    else:
        y = random.randint(0, len(user_list)-1)

    return user_list[y]


def main():
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # define private keys
    creator_private_key = contract_helper.get_private_key_from_mnemonic(creator_mnemonic)

    app_id = None
    if app_id_global is not None:
        app_id = app_id_global

    participating_users = []

    print("--------------------------------------------")
    print('What do you want to do?')
    print('1) Create Trip')
    print('2) Participate')
    print('3) Cancel Participation')
    print('4) Delete Trip')
    print('5) Get Trip State')
    x = 1
    while x != 0:
        print("--------------------------------------------")
        x = int(input())
        if x == 1:
            app_id = create_trip(algod_client, creator_private_key)
        elif x == 2:
            if app_id is None:
                misc_utils.console_log("Invalid app_id")
                continue
            test_user = get_test_user(generated_test_users, True)
            participate(algod_client, app_id, test_user.get('private_key'), test_user.get('name'))
            participating_users.append(test_user)
        elif x == 3:
            if app_id is None:
                misc_utils.console_log("Invalid app_id")
            if len(participating_users) <= 0:
                misc_utils.console_log("No user participating")
            test_user = get_test_user(participating_users, True)
            cancel_participation(algod_client, app_id,  test_user.get('private_key'), test_user.get('name'))
        elif x == 4:
            if app_id is None:
                misc_utils.console_log("Invalid app_id")
                continue
            close_trip(algod_client, app_id, creator_private_key, participating_users)
        elif x == 5:
            read_state(algod_client, app_id)
        else:
            print("Exiting..")


if __name__ == "__main__":
    main()
