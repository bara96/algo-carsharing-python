from algosdk.v2client import algod

from constants import Constants
from helpers import algo_helper
from models.IndexerManager import IndexerHelper


def main():
    mnemonic = Constants.accounts[0].get('mnemonic')
    private_key = algo_helper.get_private_key_from_mnemonic(mnemonic)
    address = algo_helper.get_address_from_private_key(private_key)

    algod_client = algod.AlgodClient(Constants.algod_token, Constants.algod_address)

    indexer = IndexerHelper()
    ids = indexer.get_app_ids_from_transactions_note(Constants.transaction_note)
    print(ids)
    app_info = indexer.get_application_from_id(ids[-1])
    print(app_info)


if __name__ == "__main__":
    main()
