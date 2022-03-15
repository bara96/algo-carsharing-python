# constants file
from utilities import account_utils

# Generated accounts for testing on sandbox
# sandbox testnet accounts
_testnet_accounts = account_utils.read_test_users("assets/testnet_accounts.csv")
# sandbox dev accounts
_dev_accounts = account_utils.read_test_users("assets/accounts.csv")

# set which accounts to use and creator account
accounts = _dev_accounts
creator_mnemonic = accounts[0].get('mnemonic')

# Algorand parameters
# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# transaction note to retrive transactions on the Indexer
transaction_note = '67c8df8c4a6ef03decdfd0f174d16641'   # carsharing md5 hash

# app id, to reuse an old app
app_id_global = 1

# The average Algorand block production time is about 4.5 seconds per block
block_speed = 4.5
