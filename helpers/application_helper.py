# helpers for calling application states on Algorand Blockchain
from algosdk import account
from algosdk.future import transaction
from helpers import algo_helper
from utils import misc_utils

# min fees is 1000
FEES = 1000


# create new application
def create_app(client, private_key, approval_program, clear_program, global_schema, local_schema, app_args):
    """
    Perform an ApplicationCreate transaction:
    Transaction to instantiate a new application
    :param client:
    :param private_key:
    :param approval_program:
    :param clear_program:
    :param global_schema:
    :param local_schema:
    :param app_args:
    :return:
    """
    misc_utils.console_log("Deploying Application......", "green")
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = FEES

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                           approval_program, clear_program,
                                           global_schema, local_schema, app_args)

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
        misc_utils.console_log(err)
        return

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    misc_utils.console_log("Application Created. New app-id: {}".format(app_id), "green")
    return app_id


# call application
def call_app(client, private_key, index, app_args):
    """
    Perform a NoOp transaction:
    Generic application calls to execute the ApprovalProgram.
    :param client:
    :param private_key:
    :param index:
    :param app_args:
    :return:
    """
    misc_utils.console_log("Calling Application......", "green")
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = FEES

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
        misc_utils.console_log(err)
        return
    misc_utils.console_log("Application called.", "green")


def opt_in_app(client, private_key, index):
    """
    Perform a OptIn transaction:
    Accounts use this transaction to begin participating in a smart contract. Participation enables local storage usage.
    :param client:
    :param private_key:
    :param index:
    """
    # declare sender
    sender = account.address_from_private_key(private_key)
    misc_utils.console_log("OptIn from account: {}".format(sender), "green")

    # get node suggested parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = FEES

    # create unsigned transaction
    txn = transaction.ApplicationOptInTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    algo_helper.wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    misc_utils.console_log("OptIn to app-id: {}".format(transaction_response["txn"]["txn"]["apid"]), "green")


def delete_app(client, private_key, index):
    """
    Perform a DeleteApplication transaction:
    Transaction to delete the application.
    :param client:
    :param private_key:
    :param index:
    """
    # declare sender
    sender = account.address_from_private_key(private_key)
    misc_utils.console_log("Deleting Application......".format(sender), "green")

    # get node suggested parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = FEES

    # create unsigned transaction
    txn = transaction.ApplicationDeleteTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    algo_helper.wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    misc_utils.console_log("Deleted Application with app-id: {}".format(transaction_response["txn"]["txn"]["apid"]),
                           "green")


def clear_app(client, private_key, index):
    """
    Perform a ClearState transaction:
    Similar to CloseOut, but the transaction will always clear a contract from the account’s balance record whether the
    program succeeds or fails.
    :param client:
    :param private_key:
    :param index:
    """
    # declare sender
    sender = account.address_from_private_key(private_key)
    misc_utils.console_log("Clearing Application from account {}".format(sender), "green")

    # get node suggested parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = FEES

    # create unsigned transaction
    txn = transaction.ApplicationClearStateTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    algo_helper.wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    misc_utils.console_log("Cleared app-id: {}".format(transaction_response["txn"]["txn"]["apid"]), "green")


def close_out_app(client, private_key, index):
    """
    Perform a CloseOut transaction:
    Accounts use this transaction to close out their participation in the contract.
    This call can fail based on the TEAL logic, preventing the account from removing the contract from its balance record.
    :param client:
    :param private_key:
    :param index:
    """
    # declare sender
    sender = account.address_from_private_key(private_key)
    misc_utils.console_log("Clearing Application from account {}".format(sender), "green")

    # get node suggested parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = FEES

    # create unsigned transaction
    txn = transaction.ApplicationCloseOutTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    algo_helper.wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    misc_utils.console_log("Cleared app-id: {}".format(transaction_response["txn"]["txn"]["apid"]), "green")
