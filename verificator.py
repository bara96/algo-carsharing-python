from pyteal import compileTeal, Mode
from constants import Constants
from helpers import algo_helper
from models.ApplicationManager import ApplicationManager
from algosdk.v2client import algod
from smart_contracts.contract_verifier import VerifierContract
from utilities import utils


def create_verificator(algod_client, private_key):
    verifier = VerifierContract()

    # compile program to TEAL assembly
    approval_program_compiled = compileTeal(
        verifier.approval_program(),
        mode=Mode.Application,
        version=5,
    )

    clear_program_compiled = compileTeal(
        verifier.clear_program(),
        mode=Mode.Application,
        version=5
    )

    # compile program to binary
    approval_program_compiled = algo_helper.compile_program(algod_client, approval_program_compiled)
    clear_state_program_compiled = algo_helper.compile_program(algod_client, clear_program_compiled)

    approval_program_hash = ""
    clear_out_program_hash = ""
    app_args = [
        approval_program_hash,
        clear_out_program_hash
    ]

    try:
        txn = ApplicationManager.create_app(algod_client,
                                            private_key,
                                            approval_program_compiled,
                                            clear_state_program_compiled,
                                            verifier.global_schema,
                                            verifier.local_schema,
                                            app_args)

        txn_response = ApplicationManager.send_transaction(algod_client, txn)
        app_id = txn_response['application-index']
        utils.console_log("Application Created. New app-id: {}".format(app_id), "green")
    except Exception as e:
        utils.console_log("Error during create_app call: {}".format(e))
        return False

    return app_id


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # define private keys
    creator_private_key = algo_helper.get_private_key_from_mnemonic(Constants.creator_mnemonic)
    algod_client = algod.AlgodClient(Constants.algod_token, Constants.algod_address)

    print("--------------------------------------------")
    print('What do you want to do?')
    print('1) Create Verifier')
    print('2) Update Verifier')
    print('4) Delete Verifier')
    print("--------------------------------------------")
    x = int(input())
    if x == 1:
        create_verificator(algod_client, creator_private_key)
    elif x == 2:
        mnemonic = Constants.creator_mnemonic
    else:
        print("Unknown action.")
