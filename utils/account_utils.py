import base64
import json

from algosdk import account, mnemonic
from algosdk import constants
from algosdk.future import transaction
from algosdk.v2client import algod

import constants as cnst
from helpers import application_helper, algo_helper
from utils import misc_utils as misc


def generate_algorand_keypair():
    """
    Generate a new Account
    """
    misc.console_log("Generating keypair..", "green")
    private_key, address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)
    print("New address: {}".format(address))
    print("New private key: {}".format(private_key))
    print("New passphrase: {}".format(passphrase))
    misc.console_log("Remember to save these values", "yellow")


def delete_user_apps(private_key):
    """
    Delete all the contracts created by the account
    :param private_key:
    """
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)

    address = algo_helper.get_address_from_private_key(private_key)
    account_info = algod_client.account_info(address)
    for app in account_info['created-apps']:
        application_helper.delete_app(algod_client, private_key, app['id'])


def clear_user_apps(private_key):
    """
    Clear all the contracts in which the account has opt-in (participating)
    :param private_key:
    """
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)

    address = algo_helper.get_address_from_private_key(private_key)
    account_info = algod_client.account_info(address)
    for app in account_info['apps-local-state']:
        application_helper.clear_app(algod_client, private_key, app['id'])


def test_transaction(private_key, my_address):
    """
    Perform a test transaction
    :param private_key:
    :param my_address:
    :return:
    """
    # default host and token for testnet sandbox
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)

    print("My address: {}".format(my_address))
    account_info = algod_client.account_info(my_address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')))

    # build transaction
    params = algod_client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = constants.MIN_TXN_FEE
    params.fee = 1000
    receiver = "5UJKXGFSP3NNLQQWYAORN7RINZZISQFBRVFLIGWFB5WF53X77YOM2ERO4E"
    note = "Hello World".encode()

    unsigned_txn = transaction.PaymentTxn(my_address, params, receiver, 1000000, None, note)

    # sign transaction
    signed_txn = unsigned_txn.sign(private_key)

    # submit transaction
    txid = algod_client.send_transaction(signed_txn)
    print("Signed transaction with txID: {}".format(txid))

    # wait for confirmation
    try:
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
    except Exception as err:
        print(err)
        return

    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))
    print("Decoded note: {}".format(base64.b64decode(
        confirmed_txn["txn"]["txn"]["note"]).decode()))

    print("Starting Account balance: {} microAlgos".format(account_info.get('amount')))
    print("Amount transfered: {} microAlgos".format(1))
    print("Fee: {} microAlgos".format(params.fee))

    account_info = algod_client.account_info(my_address)
    print("Final Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("--------------------------------------------")
    print('What do you want to do?')
    print('1) Generate keypair')
    print('2) Perform a test transaction')
    print('3) Clear Account Apps')
    print('4) Delete Account Created Apps')
    print("--------------------------------------------")
    x = int(input())
    if x == 1:
        generate_algorand_keypair()
    elif x == 2:
        mnemonic = cnst.creator_mnemonic
        private_key = algo_helper.get_private_key_from_mnemonic(mnemonic)
        address = algo_helper.get_address_from_private_key(private_key)
        test_transaction(private_key, address)
    elif x == 3:
        print('Insert the user private_key')
        private_key = input()
        clear_user_apps(private_key)
    elif x == 4:
        print('Insert the user private_key')
        private_key = input()
        delete_user_apps(private_key)
    else:
        print("Unknown action.")


