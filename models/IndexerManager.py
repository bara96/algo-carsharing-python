# class to manage algorand indexer

from algosdk.v2client import indexer


class IndexerHelper:
    indexerObj = None

    def __init__(self, host="http://localhost:8980", token=""):
        self.indexerObj = indexer.IndexerClient(indexer_token=token, indexer_address=host)

    def get_app_ids_from_transactions_note(self, note):
        """
        Get application ids from transaction with given note
        :param note:
        :return:
        """
        note_prefix = note.encode()

        # instantiate indexer client
        response = self.indexerObj.search_transactions(note_prefix=note_prefix)
        # print("note_prefix = " + json.dumps(response, indent=2, sort_keys=True))
        transactions = response['transactions'] if "transactions" in response else []

        ids = []
        for transaction in transactions:
            id = self._get_app_id_from_transaction(transaction)
            if id is not None:
                ids.append(id)
        return ids

    @staticmethod
    def _get_app_id_from_transaction(transaction):
        """
        Get application id from transaction
        :param transaction:
        :return:
        """
        return transaction["created-application-index"] if "created-application-index" in transaction else None

    def get_accounts_from_application(self, appid):
        response = self.indexerObj.search_applications(application_id=appid)
        return response
