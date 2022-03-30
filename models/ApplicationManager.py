import json
from typing import Optional

from algosdk import account
from algosdk.future import transaction
from algosdk.transaction import SignedTransaction
from algosdk.v2client import algod

from constants import Constants
from helpers import algo_helper
from utilities import utils


# class for manage application transactions on Algorand Blockchain
# will instantiate an algod_client and perform transactions calls
class ApplicationManager:
    class Variables:
        # min fees is 1000
        fees = 1000
        escrow_min_balance = 1000000
        transaction_note = Constants.transaction_note

    @classmethod
    def create_app(cls,
                   algod_client: algod.AlgodClient,
                   private_key: str,
                   approval_program,
                   clear_program,
                   global_schema,
                   local_schema,
                   app_args,
                   sign_transaction: bool = True):
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
        :param sign_transaction:
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
        txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                               approval_program, clear_program,
                                               global_schema, local_schema, app_args, note=note)
        # sign transaction
        if sign_transaction:
            txn = txn.sign(private_key)

        algo_helper.get_transaction_id(txn=txn, is_signed=sign_transaction)

        return txn

    @classmethod
    def call_app(cls,
                 algod_client: algod.AlgodClient,
                 private_key: str,
                 app_id: int,
                 app_args,
                 sign_transaction: bool = True):
        """
        Perform a NoOp transaction:
        Generic application calls to execute the ApprovalProgram.
        :param algod_client:
        :param private_key:
        :param app_id:
        :param app_args:
        :param sign_transaction:
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
        txn = transaction.ApplicationNoOpTxn(sender=sender,
                                             sp=params,
                                             index=app_id,
                                             app_args=app_args)
        # sign transaction
        if sign_transaction:
            txn = txn.sign(private_key)

        algo_helper.get_transaction_id(txn=txn, is_signed=sign_transaction)

        return txn

    @classmethod
    def opt_in_app(cls,
                   algod_client: algod.AlgodClient,
                   private_key: str,
                   app_id: int,
                   sign_transaction: bool = True):
        """
        Perform a OptIn transaction:
        Accounts use this transaction to begin participating in a smart contract.
        Participation enables local storage usage.
        :param algod_client:
        :param private_key:
        :param app_id:
        :param sign_transaction:
        """
        # declare sender
        sender = account.address_from_private_key(private_key)
        utils.console_log("OptIn from account: {}".format(sender), "green")

        # get node suggested parameters
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        # create unsigned transaction
        txn = transaction.ApplicationOptInTxn(sender, params, app_id)
        # sign transaction
        if sign_transaction:
            txn = txn.sign(private_key)

        algo_helper.get_transaction_id(txn=txn, is_signed=sign_transaction)

        return txn

    @classmethod
    def delete_app(cls,
                   algod_client: algod.AlgodClient,
                   private_key: str,
                   app_id: int,
                   sign_transaction: bool = True):
        """
        Perform a DeleteApplication transaction:
        Transaction to delete the application.
        :param algod_client:
        :param private_key:
        :param app_id:
        :param sign_transaction:
        """
        # declare sender
        sender = account.address_from_private_key(private_key)
        utils.console_log("Deleting Application......".format(sender), "green")

        # get node suggested parameters
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        # create unsigned transaction
        txn = transaction.ApplicationDeleteTxn(sender, params, app_id)
        # sign transaction
        if sign_transaction:
            txn = txn.sign(private_key)

        algo_helper.get_transaction_id(txn=txn, is_signed=sign_transaction)

        return txn

    @classmethod
    def clear_app(cls,
                  algod_client: algod.AlgodClient,
                  private_key,
                  app_id: int,
                  sign_transaction: bool = True):
        """
        Perform a ClearState transaction:
        Similar to CloseOut, but the transaction will always clear a contract from the account’s balance record whether the
        program succeeds or fails.
        :param algod_client:
        :param private_key:
        :param app_id:
        :param sign_transaction:
        """
        # declare sender
        sender = account.address_from_private_key(private_key)
        utils.console_log("Clearing Application from account {}".format(sender), "green")

        # get node suggested parameters
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        # create unsigned transaction
        txn = transaction.ApplicationClearStateTxn(sender, params, app_id)
        # sign transaction
        if sign_transaction:
            txn = txn.sign(private_key)

        algo_helper.get_transaction_id(txn=txn, is_signed=sign_transaction)

        return txn

    @classmethod
    def close_out_app(cls,
                      algod_client: algod.AlgodClient,
                      private_key: str,
                      app_id: int,
                      sign_transaction: bool = True):
        """
        Perform a CloseOut transaction:
        Accounts use this transaction to close out their participation in the contract.
        This call can fail based on the TEAL logic, preventing the account from removing the contract from its balance record.
        :param algod_client:
        :param private_key:
        :param app_id:
        :param sign_transaction:
        """
        # declare sender
        sender = account.address_from_private_key(private_key)
        utils.console_log("Clearing Application from account {}".format(sender), "green")

        # get node suggested parameters
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        # create unsigned transaction
        txn = transaction.ApplicationCloseOutTxn(sender, params, app_id)
        # sign transaction
        if sign_transaction:
            txn = txn.sign(private_key)

        algo_helper.get_transaction_id(txn=txn, is_signed=sign_transaction)

        return txn

    @classmethod
    def payment(cls,
                algod_client: algod.AlgodClient,
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
        utils.console_log("Performing a payment from account {} to account {}".format(sender_address, receiver_address),
                          "green")
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = cls.Variables.fees

        txn = transaction.PaymentTxn(sender=sender_address,
                                     sp=params,
                                     receiver=receiver_address,
                                     amt=amount)
        # sign transaction
        if sign_transaction:
            txn = txn.sign(sender_private_key)

        algo_helper.get_transaction_id(txn=txn, is_signed=sign_transaction)

        return txn

    @classmethod
    def send_transaction(cls,
                         algod_client: algod.AlgodClient,
                         txn: SignedTransaction,
                         txn_debug: bool = False):
        """
        :param algod_client:
        :param txn:
        :param txn_debug:
        """
        # submit transaction
        tx_id = algod_client.send_transaction(txn)

        # wait for confirmation
        confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id)
        print("Transaction with id {} completed".format(tx_id))
        if txn_debug:
            print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))

        return algod_client.pending_transaction_info(tx_id)

    @classmethod
    def send_group_transactions(cls,
                                algod_client: algod.AlgodClient,
                                txns: [SignedTransaction],
                                txn_debug: bool = False):
        """
        :param algod_client:
        :param txns:
        :param txn_debug:
        """
        # Atomic transfer
        tx_id = algod_client.send_transactions(txns)

        # wait for confirmation
        confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id)
        print("Transactions with id {} completed".format(tx_id))
        if txn_debug:
            print("Transactions information: {}".format(json.dumps(confirmed_txn, indent=4)))

        return algod_client.pending_transaction_info(tx_id)
