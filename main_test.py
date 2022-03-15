import json
from algosdk.v2client import algod, indexer
from helpers import algo_helper
import constants


def main():
    mnemonic = constants.accounts[0].get('mnemonic')
    private_key = algo_helper.get_private_key_from_mnemonic(mnemonic)
    address = algo_helper.get_address_from_private_key(private_key)

    algod_client = algod.AlgodClient(constants.algod_token, constants.algod_address)

    pk = algo_helper.get_private_key_from_mnemonic("brisk estate collect copper vital valve thank narrow able diesel plug fuel film negative predict pride floor box fire thank baby truck version absorb repair")
    address = algo_helper.get_address_from_private_key(pk)

    # instantiate indexer client
    myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8980")
    response = myindexer.search_transactions(note_prefix=constants.transaction_note.encode())
    #print("note_prefix = " + json.dumps(response, indent=2, sort_keys=True))

    ids = algo_helper.get_applications_from_transactions_note(constants.transaction_note)
    print(ids)


if __name__ == "__main__":
    main()
