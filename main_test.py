import json
from algosdk.v2client import algod
from helpers import algo_helper
import constants
from helpers.IndexerHelper import IndexerHelper


def main():
    mnemonic = constants.accounts[0].get('mnemonic')
    private_key = algo_helper.get_private_key_from_mnemonic(mnemonic)
    address = algo_helper.get_address_from_private_key(private_key)

    algod_client = algod.AlgodClient(constants.algod_token, constants.algod_address)

    indexer = IndexerHelper()
    ids = indexer.get_app_ids_from_transactions_note(constants.transaction_note)
    #app_info = indexer.get_accounts_from_application(ids[0])
    app_info = algod_client.application_info(ids[0])
    algo_helper.show_response(app_info)


if __name__ == "__main__":
    main()
