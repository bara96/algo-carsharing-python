# based off https://github.com/algorand/docs/blob/cdf11d48a4b1168752e6ccaf77c8b9e8e599713a/examples/smart_contracts/v2/python/stateful_smart_contracts.py

from algosdk import account
from algosdk.future import transaction
from algosdk.v2client import algod
from pyteal import compileTeal, Mode

from contract_carsharing import approval_program, clear_state_program
from helpers import contract_helper, application_helper
from utils import account_utils, misc_utils

# user declared account mnemonics
creator_mnemonic = account_utils.get_mnemonic()
user_mnemonic = "bronze wheat fine weekend piano lady toss final parrot normal father used real vast bracket open blossom sibling ride cloth gentle animal cable above kick"

# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# app id
app_id_global = 76465238


def read_state(algod_client, app_id, user_private_key=None):
    if user_private_key is not None:
        # read local state of application
        local_state = contract_helper.read_local_state(algod_client, account.address_from_private_key(user_private_key),
                                                       app_id),
        misc_utils.console_log("Local state: {}".format(local_state), 'blue')

    # read global state of application
    global_state = contract_helper.read_global_state(algod_client, app_id)
    misc_utils.console_log("Global state: {}".format(global_state), 'blue')


def cancel_participation(algod_client, app_id, user_private_key):
    app_args = [b"Cancel"]
    application_helper.call_app(algod_client, user_private_key, app_id, app_args)

    # read local state of application
    local_state = contract_helper.read_local_state(algod_client, account.address_from_private_key(user_private_key),
                                                   app_id),
    misc_utils.console_log("Local state: {}".format(local_state), 'blue')

    # read global state of application
    global_state = contract_helper.read_global_state(algod_client, app_id)
    misc_utils.console_log("Global state: {}".format(global_state), 'blue')


def participate(algod_client, app_id, user_private_key):
    # opt in to write local state
    application_helper.opt_in_app(algod_client, user_private_key, app_id)

    app_args = [b"Participate", ]
    application_helper.call_app(algod_client, user_private_key, app_id, app_args)

    # read local state of application
    local_state = contract_helper.read_local_state(algod_client, account.address_from_private_key(user_private_key),
                                                   app_id),
    misc_utils.console_log("Local state: {}".format(local_state), 'blue')

    # read global state of application
    global_state = contract_helper.read_global_state(algod_client, app_id)
    misc_utils.console_log("Global state: {}".format(global_state), 'blue')


def create_trip(algod_client, creator_private_key):
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
    global_ints = 3
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


def main():
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # define private keys
    creator_private_key = contract_helper.get_private_key_from_mnemonic(creator_mnemonic)
    user_private_key = contract_helper.get_private_key_from_mnemonic(user_mnemonic)

    app_id = None
    if app_id_global is not None:
        app_id = app_id_global

    generated_users = [
        '5Xi+rZAPUvK1nFYDjWWn/H7Zxlsjm8Do8XK9kjAk/IPtEquYsn7a1cIWwB0W/ihucolAoY1KtBrFD2xe7v/+HA=='
    ]
    print("--------------------------------------------")
    print('What do you want to do?')
    print('1) Create Trip')
    print('2) Participate')
    print('3) Cancel Participation')
    print('4) Delete Trip')
    print('5) Get Trip State')
    print('0) Exit')
    x = 1
    while x != 0:
        print("--------------------------------------------\n")
        x = int(input())
        if x == 0:
            print("Exiting..")
        elif x == 1:
            if app_id is None:
                misc_utils.console_log("Invalid app_id")
                continue
            app_id = create_trip(algod_client, creator_private_key)
        elif x == 2:
            if app_id is None:
                misc_utils.console_log("Invalid app_id")
                continue
            # generated user
            generated_user_private_key = generated_users[0]
            participate(algod_client, app_id, generated_user_private_key)
        elif x == 3:
            if app_id is None:
                misc_utils.console_log("Invalid app_id")
            if len(generated_users) <= 0:
                misc_utils.console_log("No user participating")
            cancel_participation(algod_client, app_id,  generated_users.pop())
        elif x == 4:
            if app_id is None:
                misc_utils.console_log("Invalid app_id")
                continue
            # delete application
            application_helper.delete_app(algod_client, creator_private_key, app_id)

            # clear application from user account
            application_helper.clear_app(algod_client, user_private_key, app_id)
        elif x == 5:
            read_state(algod_client, app_id)
            print("Users: ")
            print(generated_users)
        else:
            misc_utils.console_log("Unknown action.")


if __name__ == "__main__":
    main()
