# based off https://github.com/algorand/docs/blob/cdf11d48a4b1168752e6ccaf77c8b9e8e599713a/examples/smart_contracts/v2/python/stateful_smart_contracts.py

import base64
from utils import account_utils, helper

from algosdk.future import transaction
from algosdk import account
from algosdk.v2client import algod
from pyteal import compileTeal, Mode
from contract_carsharing import approval_program, clear_state_program

# user declared account mnemonics
creator_mnemonic = account_utils.get_mnemonic()
user_mnemonic = "bronze wheat fine weekend piano lady toss final parrot normal father used real vast bracket open blossom sibling ride cloth gentle animal cable above kick"

# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# app id
algo_app_id = 75868067

# create new application
def create_app(client, private_key, approval_program, clear_program, global_schema, local_schema):
    helper.console_log("Deploying Application......", "green")
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(sender, params, on_complete, \
                                           approval_program, clear_program, \
                                           global_schema, local_schema)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # wait for confirmation
    try:
        transaction_response = transaction.wait_for_confirmation(client, tx_id, 4)
        print("TXID: ", tx_id)
        print("Result confirmed in round: {}".format(transaction_response['confirmed-round']))

    except Exception as err:
        helper.console_log(err)
        return

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    helper.console_log("Application Created. New app-id: {}".format(app_id), "green")
    return app_id


# call application
def call_app(client, private_key, index, app_args):
    helper.console_log("Calling Application......", 'green')
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # wait for confirmation
    try:
        transaction_response = transaction.wait_for_confirmation(client, tx_id, 5)
        print("TXID: ", tx_id)
        print("Result confirmed in round: {}".format(transaction_response['confirmed-round']))

    except Exception as err:
        helper.console_log(err)
        return
    helper.console_log("Application called.", "green")


def main():
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # define private keys
    creator_private_key = helper.get_private_key_from_mnemonic(creator_mnemonic)
    user_private_key = helper.get_private_key_from_mnemonic(user_mnemonic)

    # declare application state storage (immutable)
    local_ints = 0
    local_bytes = 0
    global_ints = 1
    global_bytes = 0
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    ## get PyTeal approval program
    approval_program_ast = approval_program()
    # compile program to TEAL assembly
    approval_program_teal = compileTeal(approval_program_ast, mode=Mode.Application, version=5)
    # compile program to binary
    approval_program_compiled = helper.compile_program(algod_client, approval_program_teal)

    # get PyTeal clear state program
    clear_state_program_ast = clear_state_program()
    # compile program to TEAL assembly
    clear_state_program_teal = compileTeal(clear_state_program_ast, mode=Mode.Application, version=5)
    # compile program to binary
    clear_state_program_compiled = helper.compile_program(algod_client, clear_state_program_teal)

    print("--------------------------------------------")
    # create new application
    if algo_app_id is None:
        app_id = create_app(algod_client, creator_private_key, approval_program_compiled, clear_state_program_compiled,
                            global_schema, local_schema)
    else:
        app_id = algo_app_id
        app_args = ["Add"]
        call_app(algod_client, creator_private_key, app_id, app_args)

    # read local state of application
    local_state = helper.read_local_state(algod_client, account.address_from_private_key(user_private_key), app_id),
    helper.console_log("Local state: {}".format(local_state), 'blue')

    # read global state of application
    global_state = helper.read_global_state(algod_client, app_id)
    helper.console_log("Global state: {}".format(global_state), 'blue')


if __name__ == "__main__":
    main()
