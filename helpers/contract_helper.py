import base64

from algosdk import mnemonic, account


# convert 64 bit integer i to byte string
from utils import misc_utils


def intToBytes(i):
    return i.to_bytes(8, "big")

# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response['result'])


# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


# helper function that converts a private signing key from mnemonic passphrase
def get_mnemonic_from_private_key(private_key):
    mn = mnemonic.from_private_key(private_key)
    return mn


# helper function that retrieve an address from the private signing key
def get_address_from_private_key(private_key):
    address = account.address_from_private_key(private_key)
    return address


# helper function that formats global state for printing
def format_state(state):
    formatted = {}
    for item in state:
        key = item['key']
        value = item['value']
        formatted_key = base64.b64decode(key).decode('utf-8')
        if value['type'] == 1:
            # byte string
            if formatted_key == 'voted':
                formatted_value = base64.b64decode(value['bytes']).decode('utf-8')
            else:
                formatted_value = value['bytes']
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value['uint']
    return formatted


# helper function to read local state of application from user account
def read_local_state(client, addr, app_id=None, show=True):
    results = client.account_info(addr)
    for local_state in results["apps-local-state"]:
        if local_state["id"] == app_id:
            if "key-value" not in local_state:
                return None
            output = format_state(local_state["key-value"])
            if show:
                print("Local State:")
                misc_utils.console_log(output, 'blue')
            return output
    return None

# helper function to read app global state
def read_global_state(client, app_id, show=True):
    results = client.application_info(app_id)
    global_state = results['params']['global-state'] if "global-state" in results['params'] else []
    output = format_state(global_state)
    if show:
        print("Global State:")
        misc_utils.console_log(output, 'blue')
    return output


# helper function that waits for a given txid to be confirmed by the network
def wait_for_confirmation(client, txid):
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
