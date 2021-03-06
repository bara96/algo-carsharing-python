# helpers for algorand-related actions
import base64
from datetime import datetime

from algosdk import mnemonic, account, encoding

from constants import Constants
from utilities import utils


def intToBytes(value):
    """
    helper function to convert 64 bit integer i to byte string
    :param value:
    :return:
    """
    return value.to_bytes(8, "big")


def BytesToString(value: bytes):
    """
    Convert Bytes to String
    :param value:
    :return:
    """
    return base64.b64decode(value).decode('utf-8')


def BytesToAddress(value: bytes):
    """
    Convert Bytes to Address string
    :param value:
    :return:
    """
    decoded_address = base64.b64decode(value)
    return encoding.encode_address(decoded_address)


def compile_program(client, source_code):
    """
    helper function to compile program source
    :param client:
    :param source_code:
    :return:
    """
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response['result'])


def get_private_key_from_mnemonic(mn):
    """
    helper function that converts a mnemonic passphrase into a private signing key
    :param mn:
    :return:
    """
    private_key = mnemonic.to_private_key(mn)
    return private_key


def get_mnemonic_from_private_key(private_key):
    """
    helper function that converts a private signing key from mnemonic passphrase
    :param private_key:
    :return:
    """
    mn = mnemonic.from_private_key(private_key)
    return mn


def get_address_from_private_key(private_key):
    """
    helper function that retrieve an address from the private signing key
    :param private_key:
    :return:
    """
    address = account.address_from_private_key(private_key)
    return address


def format_state(state):
    """
    helper function that formats global state for printing
    :param state:
    :return:
    """
    formatted = {}
    for item in state:
        key = item['key']
        value = item['value']
        formatted_key = base64.b64decode(key).decode('utf-8')
        if value['type'] == 1:
            # byte string
            try:
                formatted_value = BytesToString(value['bytes'])
            except Exception:
                formatted_value = value['bytes']
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value['uint']
    return formatted


def read_local_state(client, addr, app_id=None, show=True):
    """
    helper function to read local state of application from user account
    :param client:
    :param addr:
    :param app_id:
    :param show:
    :return:
    """
    results = client.account_info(addr)
    for local_state in results["apps-local-state"]:
        if local_state["id"] == app_id:
            if "key-value" not in local_state:
                return None
            output = format_state(local_state["key-value"])
            if show:
                utils.console_log("Local State:", 'blue')
                print(output)
            return output
    return None


def read_global_state(client, app_id, to_array=True, show=True):
    """
    helper function to read app global state
    :param client:
    :param app_id:
    :param show:
    :param to_array:
    :return:
    """
    results = client.application_info(app_id)
    global_state = results['params']['global-state'] if "global-state" in results['params'] else []
    creator = results['params']['creator'] if "creator" in results['params'] else None
    approval_program = results['params']['approval-program'] if "approval-program" in results['params'] else None
    clear_state_program = results['params']['clear-state-program'] if "clear-state-program" in results['params'] else None

    output = format_state(global_state)
    if to_array:
        output = utils.toArray(output)

    if show:
        utils.console_log("Global State:", 'blue')
        print(output)
    return output, creator, approval_program, clear_state_program


def wait_for_confirmation(client, txid):
    """
    helper function that waits for a given txid to be confirmed by the network
    :param client:
    :param txid:
    :return:
    """
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(
        "Transaction {} confirmed in round {}.".format(
            txid, txinfo.get("confirmed-round")
        )
    )
    return txinfo


def datetime_to_rounds(algod_client, given_date):
    """
    Get the first valid round from a datetime
    :param algod_client:
    :param given_date:
    :return:
    """
    status = algod_client.status()
    now = datetime.now()
    current_time = datetime.strptime(now.strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
    given_date = datetime.strptime(given_date, '%Y-%m-%d %H:%M')
    difference_seconds = given_date.timestamp() - current_time.timestamp()
    if difference_seconds < 0:
        return 0
    n_blocks_produced = difference_seconds / Constants.block_speed
    first_valid_round = status["last-round"] + n_blocks_produced
    return round(first_valid_round)


def get_transaction_id(txn, is_signed: bool = True, show: bool = True):
    """
    Get transaction id
    :param txn:
    :param is_signed:
    :param show:
    :return:
    """
    if is_signed:
        tx_id = txn.transaction.get_txid()
    else:
        tx_id = txn.get_txid()

    if show:
        print("TXID: ", tx_id)

    return tx_id