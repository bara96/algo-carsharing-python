from pyteal import *
import algosdk


class CarSharingContract:
    class Variables:
        creator_address = Bytes("creator")              # Bytes
        creator_name = Bytes("creator_name")            # Bytes
        departure_address = Bytes("departure_address")  # Bytes
        arrival_address = Bytes("arrival_address")      # Bytes
        departure_date = Bytes("departure_date")        # Int
        arrival_date = Bytes("arrival_date")            # Int
        available_seats = Bytes("available_seats")      # Int
        trip_cost = Bytes("trip_cost")                  # Int
        app_state = Bytes("trip_state")                 # Int
        escrow_address = Bytes("escrow_address")        # Bytes
        # Local State Keys
        is_participating = Bytes("is_participating")    # Int

    class AppMethods:
        initialize_escrow = "initializeEscrow"
        cancel_trip = "cancelTrip"
        participate_trip = "participateTrip"
        cancel_trip_participation = "cancelParticipation"

    class AppState:
        not_initialized = Int(0)
        initialized = Int(1)
        started = Int(2)

    class UserState:
        participating = Int(1)
        not_participating = Int(0)

    def application_start(self):
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)

        handle_noop = Seq(
            Cond(
                [Txn.application_args[0] == Bytes(self.AppMethods.initialize_escrow),
                 self.initialize_escrow(escrow_address=Txn.application_args[1])],

                [Txn.application_args[0] == Bytes(self.AppMethods.participate_trip),
                 self.participate_trip()],

                [Txn.application_args[0] == Bytes(self.AppMethods.cancel_trip_participation),
                 self.cancel_participation()]
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
        valid_number_of_args = Txn.application_args.length() == Int(7)

        return Seq([
            Assert(valid_number_of_args),  # 3 Bytes, 4 Int
            App.globalPut(self.Variables.creator_address, Txn.sender()),  # 1 Bytes
            App.globalPut(self.Variables.creator_name, Txn.application_args[0]),
            App.globalPut(self.Variables.departure_address, Txn.application_args[1]),
            App.globalPut(self.Variables.arrival_address, Txn.application_args[2]),
            App.globalPut(self.Variables.departure_date, Btoi(Txn.application_args[3])),
            App.globalPut(self.Variables.arrival_date, Btoi(Txn.application_args[4])),
            App.globalPut(self.Variables.trip_cost, Btoi(Txn.application_args[5])),
            App.globalPut(self.Variables.available_seats, Btoi(Txn.application_args[6])),
            App.globalPut(self.Variables.app_state, self.AppState.not_initialized),
            Assert(Global.round() <= App.globalGet(self.Variables.departure_date)),  # check dates are valid
            Assert(App.globalGet(self.Variables.departure_date) < App.globalGet(self.Variables.arrival_date)),
            Assert(App.globalGet(self.Variables.available_seats) > Int(0)),  # at least a seat
            Return(Int(1))
        ])

    def initialize_escrow(self, escrow_address):
        """
        Application call from the app_admin.
        :return:
        """
        curr_escrow_address = App.globalGetEx(Int(0), self.Variables.escrow_address)
        valid_number_of_transactions = Global.group_size() == Int(1)
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)

        update_state = Seq([
            App.globalPut(self.Variables.escrow_address, escrow_address),
            App.globalPut(self.Variables.app_state, self.AppState.initialized),
        ])
        return Seq([
            curr_escrow_address,
            Assert(curr_escrow_address.hasValue() == Int(0)),
            Assert(valid_number_of_transactions),
            Assert(is_creator),
            update_state,
            Return(Int(1))
        ])

    def opt_in(self):
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)
        return Seq([
            Assert(Not(is_creator)),
            Assert(App.globalGet(self.Variables.app_state) == self.AppState.initialized),
            Assert(Global.round() <= App.globalGet(self.Variables.departure_date)),
            Assert(App.globalGet(self.Variables.available_seats) > Int(0)),
            Return(Int(1))
        ])

    def participate_trip(self):
        get_participant_state = App.localGetEx(Int(0), App.id(), self.Variables.is_participating)
        available_seats = App.globalGet(self.Variables.available_seats)
        valid_number_of_transactions = Global.group_size() == Int(2)
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)

        # check if user can participate
        can_participate = And(
            App.globalGet(self.Variables.app_state) == self.AppState.initialized,
            Not(is_creator),
            App.globalGet(self.Variables.available_seats) > Int(0),  # check if there is an available seat
            Global.round() <= App.globalGet(self.Variables.departure_date),  # check if trip is started
            valid_number_of_transactions,
        )

        # check if the payment is valid
        valid_payment = And(
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].receiver() == App.globalGet(self.Variables.escrow_address),
            Gtxn[1].amount() == App.globalGet(self.Variables.trip_cost),
            Gtxn[1].sender() == Gtxn[0].sender(),
        )

        update_state = Seq([
            # check if user is not already participating
            get_participant_state,
            Assert(
                Or(
                    Not(get_participant_state.hasValue()),
                    get_participant_state.value() == Int(0),
                ),
            ),
            # update state
            App.globalPut(self.Variables.available_seats, available_seats - Int(1)),    # decrease seats
            App.localPut(Int(0), self.Variables.is_participating, Int(1)),              # set user as participating
        ])

        return Seq([
            Assert(can_participate),
            Assert(valid_payment),
            update_state,
            Return(Int(1))
        ])

    def cancel_participation(self):
        get_participant_state = App.localGetEx(Int(0), App.id(), self.Variables.is_participating)
        available_seats = App.globalGet(self.Variables.available_seats)
        valid_number_of_transactions = Global.group_size() == Int(2)
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)

        # check if user can cancel participation
        can_cancel = And(
            App.globalGet(self.Variables.app_state) == self.AppState.initialized,
            Not(is_creator),
            Global.round() <= App.globalGet(self.Variables.departure_date),  # check if trip is started
            valid_number_of_transactions,
        )

        valid_refund = And(
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].receiver() == Gtxn[0].sender(),
            Gtxn[1].amount() == App.globalGet(self.Variables.trip_cost),
            Gtxn[1].sender() == App.globalGet(self.Variables.escrow_address),
        )

        update_state = Seq([
            # check if user is already participating
            get_participant_state,
            Assert(
                And(
                    get_participant_state.hasValue(),
                    get_participant_state.value() == Int(1),
                )
            ),
            # update state
            App.globalPut(self.Variables.available_seats, available_seats + Int(1)),    # increase seats
            App.localPut(Int(0), self.Variables.is_participating, Int(0)),              # set user as not participating
            Return(Int(1))
        ])

        return Seq([
            Assert(can_cancel),
            Assert(valid_refund),
            update_state,
            Return(Int(1))
        ])

    def start_trip(self):
        can_start = And(
            App.globalGet(self.Variables.app_state) == self.AppState.initialized,
            Txn.sender() == App.globalGet(self.Variables.creator_address),  # creator only can perform this action
            Global.round() >= App.globalGet(self.Variables.departure_date),  # check if trip is started
        )

        update_state = Seq([
            App.globalPut(self.Variables.app_state, self.AppState.started),
            Return(Int(1))
        ])

        return If(can_start).Then(update_state).Else(Return(Int(0)))

    def approval_program(self):
        return self.application_start()

    def clear_program(self):
        return Return(Int(1))

    @property
    def global_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=6,
                                                      num_byte_slices=5)

    @property
    def local_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=1,
                                                      num_byte_slices=0)
