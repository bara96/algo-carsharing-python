import os

from algosdk.v2client import algod
from pyteal import compileTeal, Mode

from constants import Constants
from helpers import algo_helper
from models.Trip import Trip
from smart_contracts.contract_carsharing import CarSharingContract


def main():
    algod_client = algod.AlgodClient(Constants.algod_token, Constants.algod_address)
    app = Trip(algod_client=algod_client)

    # compile program to TEAL assembly
    approval_program_compiled = compileTeal(
        app.app_contract.approval_program(),
        mode=Mode.Application,
        version=app.teal_version,
    )

    clear_program_compiled = compileTeal(
        app.app_contract.clear_program(),
        mode=Mode.Application,
        version=app.teal_version
    )

    if not os.path.isdir("compiled"):
        os.mkdir("compiled")

    # compile program to binary
    with open("compiled/carsharing_approval.teal", "w") as f:
        f.write(approval_program_compiled)

    with open("compiled/carsharing_clear_state.teal", "w") as f:
        f.write(clear_program_compiled)


if __name__ == "__main__":
    main()
