import base64
import json
import os

from algosdk import account, mnemonic
from algosdk import constants
from algosdk.future import transaction
from algosdk.v2client import algod
from dotenv import load_dotenv

from utils import misc_utils as misc


def generate_algorand_keypair():
    misc.console_log("Generating keypair..", "green")
    private_key, address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)
    print("New address: {}".format(address))
    print("New private key: {}".format(private_key))
    print("New passphrase: {}".format(passphrase))
    misc.console_log("Save values into .env", "yellow")


def get_address():
    load_dotenv()
    return os.getenv('ADDRESS')


def get_key():
    load_dotenv()
    return os.getenv('PRIVATE_KEY')


def get_mnemonic():
    load_dotenv()
    return os.getenv('MNEMONIC')


def read_algorand_keypair(show=False):
    misc.console_log("Reading keypair..", "green")
    address = get_address()
    private_key = get_key()
    passphrase = get_mnemonic()

    if show:
        print("Address: {}".format(address))
        print("Private key: {}".format(private_key))
        print("Passphrase: {}".format(passphrase))
    return address, private_key


def test_transaction(private_key, my_address):
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
    print('What do you want to do?')
    print('1) Generate keypair')
    print('2) Read existing keypair')
    print('3) Perform a transaction')
    x = int(input())
    if x == 1:
        generate_algorand_keypair()
    elif x == 2:
        read_algorand_keypair(True)
    elif x == 3:
        address, private_key = read_algorand_keypair()
        test_transaction(private_key, address)
    else:
        print("Unknown action.")
