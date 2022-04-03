from constants import Constants
from helpers import algo_helper
from algosdk.v2client import algod

from models.Verifier import Verifier
from utilities import utils
from algosdk.v2client import algod

from constants import Constants
from helpers import algo_helper
from models.Verifier import Verifier
from utilities import utils

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # define private keys
    creator_private_key = algo_helper.get_private_key_from_mnemonic(Constants.creator_mnemonic)
    algod_client = algod.AlgodClient(Constants.algod_token, Constants.algod_address)

    app_id = Constants.verificator_app_id
    verifier = Verifier(algod_client=algod_client, app_id=app_id)

    approval_program_hash = "BSADAQADJggPYXZhaWxhYmxlX3NlYXRzB2NyZWF0b3IOZGVwYXJ0dXJlX2RhdGUKdHJpcF9zdGF0ZQ5lc2Nyb3dfYWRkcmVzcxBpc19wYXJ0aWNpcGF0aW5nCXRyaXBfY29zdAxhcnJpdmFsX2RhdGUxGCMSQAFlMRkiEkABRTEZIxJAAB0xGYEEEkAADzEZgQUSQAABADEAKWQSQzEAKWQSQzYaAIAQaW5pdGlhbGl6ZUVzY3JvdxJAAOU2GgCAD3BhcnRpY2lwYXRlVHJpcBJAAHM2GgCAE2NhbmNlbFBhcnRpY2lwYXRpb24SQAABACtkIhIxAClkEhQQMgYqZA4QMgQkEhBEMwEQIhIzAQczAAASEDMBCCcGZBIQMwEAJwRkEhBEIzIIJwVjNQQ1BTQENAUiEhBEKChkIghnIycFI2YiQyJDK2QiEjEAKWQSFBAoZCMNEDIGKmQOEDIEJBIQRDMBECISMwEHJwRkEhAzAQgnBmQSEDMBADMAABIQRCMyCCcFYzUCNQM0AhQ0AyMSEUQoKGQiCWcjJwUiZiJDIycEZTUANQE0ACMSRDIEIhJEMQApZBJEJwQ2GgFnKyJnIkMxAClkEhREK2QiEkQyBipkDkQoZCMNRCJDMRuBBxJEKTEAZ4AMY3JlYXRvcl9uYW1lNhoAZ4ARZGVwYXJ0dXJlX2FkZHJlc3M2GgFngA9hcnJpdmFsX2FkZHJlc3M2GgJnKjYaAxdnJwc2GgQXZycGNhoFF2coNhoGF2crI2cyBipkDkQqZCcHZAxEKGQjDUQiQw=="
    clear_state_program_hash = "BYEBQw=="

    print("--------------------------------------------")
    print('What do you want to do?')
    print('1) Create Verifier')
    print('2) Update Verifier')
    print('4) Delete Verifier')
    print("--------------------------------------------")
    x = int(input())
    if x == 1:
        verifier.create_verifier(creator_private_key=creator_private_key,
                                 approval_program_hash=approval_program_hash,
                                 clear_state_program_hash=clear_state_program_hash)
    elif x == 2:
        if verifier.app_id is None:
            utils.console_log("Invalid app_id")
            exit(0)
        verifier.update_verifier(creator_private_key=creator_private_key,
                                 approval_program_hash=approval_program_hash,
                                 clear_state_program_hash=clear_state_program_hash)
    elif x == 3:
        if verifier.app_id is None:
            utils.console_log("Invalid app_id")
            exit(0)
        verifier.delete_verifier(creator_private_key=creator_private_key)
    else:
        print("Unknown action.")
