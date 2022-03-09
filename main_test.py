from datetime import datetime

from algosdk.v2client import algod
from helpers import algo_helper
import constants


def main():
    mnemonic = "bronze wheat fine weekend piano lady toss final parrot normal father used real vast bracket open blossom sibling ride cloth gentle animal cable above kick"
    private_key = algo_helper.get_private_key_from_mnemonic(mnemonic)
    address = algo_helper.get_address_from_private_key(private_key)

    algod_client = algod.AlgodClient(constants.algod_token, constants.algod_address)

    print(algod_client.account_info(address))


if __name__ == "__main__":
    main()