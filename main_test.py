from datetime import datetime

from algosdk.v2client import algod

import constants
from helpers import contract_helper


def main():
    algod_client = algod.AlgodClient(constants.algod_token, constants.algod_address)

    tripStartDate = datetime.strptime("2022-03-20 12:00", '%Y-%m-%d %H:%M')
    tripEndDate = datetime.strptime("2022-03-20 15:00", '%Y-%m-%d %H:%M')

    print(contract_helper.datetime_to_rounds(algod_client, "2022-03-08 22:00"))

    print(contract_helper.datetime_to_rounds(algod_client, "2022-03-20 15:00"))


if __name__ == "__main__":
    main()