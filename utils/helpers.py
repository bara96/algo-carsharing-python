import base64

from algosdk import mnemonic, account


def console_log(message, color='red', newline=False):
    """
    Print a colored console message
    :param message:
    :param color:
    :param newline:
    """
    nl = ''
    if newline:
        nl = '\n'
    if color == 'red':
        print("{}\033[91m{}\033[0m".format(nl, message))
    elif color == 'green':
        print("{}\033[92m{}\033[0m".format(nl, message))
    elif color == 'yellow':
        print("{}\033[93m{}\033[0m".format(nl, message))
    elif color == 'blue':
        print("{}\033[94m{}\033[0m".format(nl, message))


# convert 64 bit integer i to byte string
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


# helper function to read app local state
def read_local_state(client, addr, app_id):
    results = client.account_info(addr)
    for local_state in results["apps-local-state"]:
        if local_state["id"] == app_id:
            if "key-value" not in local_state:
                return {}
            return format_state(local_state["key-value"])
    return {}


# helper function to read app global state
def read_global_state(client, addr, app_id):
    results = client.account_info(addr)
    apps_created = results["created-apps"]
    for app in apps_created:
        if app["id"] == app_id:
            return format_state(app["params"]["global-state"])
    return {}


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
