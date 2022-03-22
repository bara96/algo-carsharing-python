# constants file
def read_test_users(filename):
    """
    Read test accounts from file
    :return:
    """
    import csv
    accounts = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            accounts.append({
                'name': row['name'],
                'mnemonic': row['mnemonic'],
            })

    return accounts


class Constants:
    # Generated accounts for testing on sandbox
    # sandbox testnet accounts
    testnet_accounts = read_test_users("assets/testnet_accounts.csv")
    # sandbox dev accounts
    dev_accounts = read_test_users("assets/accounts.csv")

    # set which accounts to use and creator account
    accounts = dev_accounts
    creator_mnemonic = accounts[0].get('mnemonic')

    # Algorand parameters
    # user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    # transaction note to retrive transactions on the Indexer
    transaction_note = '67c8df8c4a6ef03decdfd0f174d16641'  # carsharing md5 hash

    # The average Algorand block production time is about 4.5 seconds per block
    block_speed = 4.5
