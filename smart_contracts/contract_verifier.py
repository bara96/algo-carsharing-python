from pyteal import *
import algosdk

class VerifierContract:
    class Variables:
        creator_address = Bytes("creator")                         # Bytes
        approval_program_hash = Bytes("approval_program_hash")     # Bytes
        clear_out_program_hash = Bytes("clear_out_program_hash")   # Bytes

    def application_start(self):
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)

        actions = Cond(
            [Txn.application_id() == Int(0), self.app_create()],
            [Txn.on_completion() == OnComplete.NoOp, self.app_check()],
            [Txn.on_completion() == OnComplete.UpdateApplication, self.app_update()],
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        )

        return actions

    def app_check(self):
        return Seq([
            Assert(Global.group_size() == Int(3)),
            Assert(Gtxn[2].approval_program() == App.globalGet(self.Variables.approval_program_hash)),
            Assert(Gtxn[2].clear_state_program() == App.globalGet(self.Variables.clear_out_program_hash)),
        ])

    def app_create(self):
        """
        CreateAppTxn with 2 arguments: asa_owner, app_admin.
        The foreign_assets array should have 1 asa_id which will be the id of the NFT of interest.
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
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)
        valid_number_of_args = Txn.application_args.length() == Int(2)

        Seq([
            Assert(valid_number_of_args),
            Assert(is_creator),
            App.globalPut(self.Variables.approval_program_hash, Txn.application_args[0]),
            App.globalPut(self.Variables.clear_out_program_hash, Txn.application_args[1]),
            Return(Int(1))
        ])

    def approval_program(self):
        return self.application_start()

    def clear_program(self):
        return Return(Int(1))

    @property
    def global_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=0,
                                                      num_byte_slices=3)

    @property
    def local_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=0,
                                                      num_byte_slices=0)
