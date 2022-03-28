import base64
import json

from algosdk import account
from algosdk.future import transaction

from constants import Constants
from helpers import algo_helper
from utilities import utils


# class for manage application transactions on Algorand Blockchain
# will instantiate an algod_client and perform transactions calls
class ApplicationManager:
    class Variables:
        # min fees is 1000
        fees = 1000
        transaction_note = Constants.transaction_note

    @classmethod
    def create_app(cls,
                   algod_client,
                   private_key,
                   approval_program,
                   clear_program,
                   global_schema,
                   local_schema,
                   app_args):
        """
        Perform an ApplicationCreate transaction:
        Transaction to instantiate a new application
        :param algod_client:
        :param private_key:
        :param approval_program:
        :param clear_program:
        :param global_schema:
        :param local_schema:
        :param app_args:
        :return:
        """
        utils.console_log("Deploying Application......", "green")
        # define sender as creator
        sender = account.address_from_private_key(private_key)

        # declare on_complete as NoOp
        on_complete = transaction.OnComplete.NoOpOC.real

        # get node suggested parameters
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees
        note = cls.Variables.transaction_note.encode()

        # create unsigned transaction
        unsigned_txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                                        approval_program, clear_program,
                                                        global_schema, local_schema, app_args, note=note)

        # sign transaction
        signed_txn = unsigned_txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()

        # send transaction
        algod_client.send_transactions([signed_txn])

        # wait for confirmation
        try:
            transaction_response = transaction.wait_for_confirmation(algod_client, tx_id, 4)
            print("TXID: ", tx_id)
            print("Result confirmed in round: {}".format(transaction_response['confirmed-round']))

        except Exception as err:
            utils.console_log(err)
            return

        # display results
        transaction_response = algod_client.pending_transaction_info(tx_id)
        app_id = transaction_response['application-index']
        utils.console_log("Application Created. New app-id: {}".format(app_id), "green")
        return app_id

    @classmethod
    def call_app(cls, algod_client, private_key, index: int, app_args):
        """
        Perform a NoOp transaction:
        Generic application calls to execute the ApprovalProgram.
        :param private_key:
        :param index:
        :param app_args:
        :return:
        """
        utils.console_log("Calling Application......", "green")
        # declare sender
        sender = account.address_from_private_key(private_key)

        # get node suggested parameters
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        # create unsigned transaction
        txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args)

        # sign transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()

        # send transaction
        algod_client.send_transactions([signed_txn])

        # wait for confirmation
        try:
            transaction_response = transaction.wait_for_confirmation(algod_client, tx_id, 5)
            print("TXID: ", tx_id)
            print("Result confirmed in round: {}".format(transaction_response['confirmed-round']))

        except Exception as err:
            utils.console_log(err)
            return
        utils.console_log("Application called.", "green")

    @classmethod
    def opt_in_app(cls, algod_client, private_key, index: int):
        """
        Perform a OptIn transaction:
        Accounts use this transaction to begin participating in a smart contract. Participation enables local storage usage.
        :param algod_client:
        :param private_key:
        :param index:
        """
        # declare sender
        sender = account.address_from_private_key(private_key)
        utils.console_log("OptIn from account: {}".format(sender), "green")

        # get node suggested parameters
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        # create unsigned transaction
        txn = transaction.ApplicationOptInTxn(sender, params, index)

        # sign transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()

        # send transaction
        algod_client.send_transactions([signed_txn])

        # await confirmation
        algo_helper.wait_for_confirmation(algod_client, tx_id)

        # display results
        transaction_response = algod_client.pending_transaction_info(tx_id)
        utils.console_log("OptIn to app-id: {}".format(transaction_response["txn"]["txn"]["apid"]), "green")

    @classmethod
    def delete_app(cls, algod_client, private_key, index: int):
        """
        Perform a DeleteApplication transaction:
        Transaction to delete the application.
        :param algod_client:
        :param private_key:
        :param index:
        """
        # declare sender
        sender = account.address_from_private_key(private_key)
        utils.console_log("Deleting Application......".format(sender), "green")

        # get node suggested parameters
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        # create unsigned transaction
        txn = transaction.ApplicationDeleteTxn(sender, params, index)

        # sign transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()

        # send transaction
        algod_client.send_transactions([signed_txn])

        # await confirmation
        algo_helper.wait_for_confirmation(algod_client, tx_id)

        # display results
        transaction_response = algod_client.pending_transaction_info(tx_id)
        utils.console_log("Deleted Application with app-id: {}".format(transaction_response["txn"]["txn"]["apid"]),
                          "green")

    @classmethod
    def clear_app(cls, algod_client, private_key, index: int):
        """
        Perform a ClearState transaction:
        Similar to CloseOut, but the transaction will always clear a contract from the account’s balance record whether the
        program succeeds or fails.
        :param algod_client:
        :param private_key:
        :param index:
        """
        # declare sender
        sender = account.address_from_private_key(private_key)
        utils.console_log("Clearing Application from account {}".format(sender), "green")

        # get node suggested parameters
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        # create unsigned transaction
        txn = transaction.ApplicationClearStateTxn(sender, params, index)

        # sign transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()

        # send transaction
        algod_client.send_transactions([signed_txn])

        # await confirmation
        algo_helper.wait_for_confirmation(algod_client, tx_id)

        # display results
        transaction_response = algod_client.pending_transaction_info(tx_id)
        utils.console_log("Cleared app-id: {}".format(transaction_response["txn"]["txn"]["apid"]), "green")

    @classmethod
    def close_out_app(cls, algod_client, private_key, index: int):
        """
        Perform a CloseOut transaction:
        Accounts use this transaction to close out their participation in the contract.
        This call can fail based on the TEAL logic, preventing the account from removing the contract from its balance record.
        :param algod_client:
        :param private_key:
        :param index:
        """
        # declare sender
        sender = account.address_from_private_key(private_key)
        utils.console_log("Clearing Application from account {}".format(sender), "green")

        # get node suggested parameters
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        # create unsigned transaction
        txn = transaction.ApplicationCloseOutTxn(sender, params, index)

        # sign transaction
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()

        # send transaction
        algod_client.send_transactions([signed_txn])

        # await confirmation
        algo_helper.wait_for_confirmation(algod_client, tx_id)

        # display results
        transaction_response = algod_client.pending_transaction_info(tx_id)
        utils.console_log("Cleared app-id: {}".format(transaction_response["txn"]["txn"]["apid"]), "green")

    @classmethod
    def payment(cls,
                algod_client,
                sender_address: str,
                receiver_address: str,
                amount: int,
                sender_private_key: str,
                sign_transaction: bool = True):
        """
        Creates a payment transaction in ALGOs.
        :param algod_client:
        :param sender_address:
        :param receiver_address:
        :param amount:
        :param sender_private_key:
        :param sign_transaction:
        :return:
        """

        utils.console_log("Performing a payment from account {} to account {}".format(sender_address, receiver_address), "green")
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        txn = transaction.PaymentTxn(sender=sender_address,
                                     sp=params,
                                     receiver=receiver_address,
                                     amt=amount)

        if sign_transaction:
            txn = txn.sign(private_key=sender_private_key)

            # submit transaction
            txid = algod_client.send_transaction(txn)

            # wait for confirmation
            confirmed_txn = transaction.wait_for_confirmation(algod_client, txid)

            utils.console_log("Transaction with id {} completed".format(txid), "green")
            print("Amount transfered: {} microAlgos".format(amount))
            print("Fee: {} microAlgos".format(params.fee))
            print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))
