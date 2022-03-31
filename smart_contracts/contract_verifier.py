import algosdk
from pyteal import *


class VerifierContract:
    class Variables:
        creator_address = Bytes("creator")  # Bytes
        approval_program_hash = Bytes("approval_program_hash")  # Bytes
        clear_out_program_hash = Bytes("clear_out_program_hash")  # Bytes

    def application_start(self):
        """
        Start the application, check with transaction to execute
        :return: 
        """
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)

        actions = Cond(
            [Txn.application_id() == Int(0), self.app_create()],
            [Txn.on_completion() == OnComplete.OptIn, Return(Int(0))],
            [Txn.on_completion() == OnComplete.NoOp, self.app_check()],
            [Txn.on_completion() == OnComplete.UpdateApplication, self.app_update()],
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        )

        return actions

    def app_create(self):
        """
        CreateAppTxn
        Set the global_state of the app with given params
        Perform some checks for params validity
        :return:
        """
        valid_number_of_args = Txn.application_args.length() == Int(2)

        return Seq([
            Assert(valid_number_of_args),
            App.globalPut(self.Variables.creator_address, Txn.sender()),
            App.globalPut(self.Variables.approval_program_hash, Txn.application_args[0]),
            App.globalPut(self.Variables.clear_out_program_hash, Txn.application_args[1]),
            Return(Int(1))
        ])

    def app_update(self):
        """
        UpdateTxn
        Update contract programs and global_state
        """
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)
        valid_number_of_args = Txn.application_args.length() == Int(2)

        return Seq([
            Assert(valid_number_of_args),
            Assert(is_creator),
            App.globalPut(self.Variables.creator_address, Txn.sender()),
            App.globalPut(self.Variables.approval_program_hash, Txn.application_args[0]),
            App.globalPut(self.Variables.clear_out_program_hash, Txn.application_args[1]),
            Return(Int(1))
        ])

    def app_check(self):
        """
        NoOpTxn
        Check if the approval_program and clear_state_program of the trip_contract is as expected
        :return: 
        """
        return Seq([
            Assert(Global.group_size() == Int(3)),
            Assert(Gtxn[2].approval_program() == App.globalGet(self.Variables.approval_program_hash)),
            Assert(Gtxn[2].clear_state_program() == App.globalGet(self.Variables.clear_out_program_hash)),
        ])
    
    def approval_program(self):
        """
        approval_program of the contract
        :return:
        """
        return self.application_start()

    def clear_program(self):
        """
        clear_state_program of the contract
        :return:
        """
        return Return(Int(1))

    @property
    def global_schema(self):
        """
        global_schema of the contract
        :return:
        """
        return algosdk.future.transaction.StateSchema(num_uints=0,
                                                      num_byte_slices=3)

    @property
    def local_schema(self):
        """
        local_schema of the contract
        :return:
        """
        return algosdk.future.transaction.StateSchema(num_uints=0,
                                                      num_byte_slices=0)
