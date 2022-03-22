from pyteal import *
import algosdk


class CarSharingContractASC1:
    class Variables:
        creator_key = Bytes("creator")
        creator_name_key = Bytes("creator_name")
        departure_address_key = Bytes("departure_address")
        arrival_address_key = Bytes("arrival_address")
        departure_date_key = Bytes("departure_date")
        arrival_date_key = Bytes("arrival_date")
        available_seats_key = Bytes("available_seats")
        trip_cost_key = Bytes("trip_cost")
        # Local State Keys
        is_participating_key = Bytes("is_participating")

    class AppMethods:
        cancel_trip = "cancelTrip"
        participate_trip = "participateTrip"
        cancel_trip_participation = "cancelParticipation"

    class AppState:
        not_initialized = Int(0)
        active = Int(1)

    class UserState:
        participating = Int(1)
        not_participating = Int(0)

    def application_start(self):
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_key)

        handle_noop = Seq(
            Assert(Global.group_size() == Int(1)),
            Cond(
                [Txn.application_args[0] == Bytes(self.AppMethods.participate_trip), self.participate_trip()],
                [Txn.application_args[0] == Bytes(self.AppMethods.cancel_trip_participation), self.cancel_participation()]
            )
        )

        actions = Cond(
            [Txn.application_id() == Int(0), self.app_create()],
            [Txn.on_completion() == OnComplete.OptIn, self.opt_in()],
            [Txn.on_completion() == OnComplete.NoOp, handle_noop],
            [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_creator)],
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],

        )

        return actions

    def app_create(self):
        """
        CreateAppTxn with 2 arguments: asa_owner, app_admin.
        The foreign_assets array should have 1 asa_id which will be the id of the NFT of interest.
        :return:
        """
        return Seq([
            App.globalPut(self.Variables.creator_key, Txn.sender()),  # 1 Bytes
            Assert(Txn.application_args.length() == Int(7)),  # 3 Bytes, 4 Int
            App.globalPut(self.Variables.creator_name_key, Txn.application_args[0]),
            App.globalPut(self.Variables.departure_address_key, Txn.application_args[1]),
            App.globalPut(self.Variables.arrival_address_key, Txn.application_args[2]),
            App.globalPut(self.Variables.departure_date_key, Btoi(Txn.application_args[3])),
            App.globalPut(self.Variables.arrival_date_key, Btoi(Txn.application_args[4])),
            App.globalPut(self.Variables.trip_cost_key, Btoi(Txn.application_args[5])),
            App.globalPut(self.Variables.available_seats_key, Btoi(Txn.application_args[6])),
            Assert(Global.round() <= App.globalGet(self.Variables.departure_date_key)),  # check dates are valid
            Assert(App.globalGet(self.Variables.departure_date_key) < App.globalGet(self.Variables.arrival_date_key)),
            Assert(App.globalGet(self.Variables.available_seats_key) > Int(0)),  # at least a seat
            Return(Int(1))
        ])

    def opt_in(self):
        return Seq([
            Assert(Global.round() <= App.globalGet(self.Variables.departure_date_key)),
            Assert(App.globalGet(self.Variables.available_seats_key) > Int(0)),
            Return(Int(1))
        ])

    def participate_trip(self):
        get_participant_state = App.localGetEx(Int(0), App.id(), self.Variables.is_participating_key)

        participant_name = Txn.application_args[1]
        available_seats = App.globalGet(self.Variables.available_seats_key)
        return Seq(
            Assert(App.globalGet(self.Variables.available_seats_key) > Int(0)),  # check if there is an available seat
            Assert(Global.round() <= App.globalGet(self.Variables.departure_date_key)),  # check if trip is finished
            get_participant_state,
            Assert(
                Or(
                    Not(get_participant_state.hasValue()),
                    get_participant_state.value() == Int(0)
                )
            ),  # check if already participating
            App.globalPut(self.Variables.available_seats_key, available_seats - Int(1)),
            App.localPut(Int(0), self.Variables.is_participating_key, Int(1)),
            Return(Int(1))
        )

    def cancel_participation(self):
        get_participant_state = App.localGetEx(Int(0), App.id(), self.Variables.is_participating_key)
        available_seats = App.globalGet(self.Variables.available_seats_key)

        return Seq(
            Assert(Global.round() <= App.globalGet(self.Variables.departure_date_key)),  # check if trip is finished
            get_participant_state,
            Assert(
                And(
                    get_participant_state.hasValue(),
                    get_participant_state.value() == Int(1)
                )
            ),  # check if not participating
            App.globalPut(self.Variables.available_seats_key, available_seats + Int(1)),
            App.localPut(Int(0), self.Variables.is_participating_key, Int(0)),
            Return(Int(1))
        )

    def approval_program(self):
        return self.application_start()

    def clear_program(self):
        return Return(Int(1))

    @property
    def global_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=4,  # 4 for setup
                                                      num_byte_slices=5)  # 4 for setup + 1 for participants

    @property
    def local_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=1,  # for participating
                                                      num_byte_slices=0)
