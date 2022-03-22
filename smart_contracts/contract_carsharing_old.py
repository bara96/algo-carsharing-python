from pyteal import *


# Handle each possible OnCompletion type. We don't have to worry about
# handling ClearState, because the ClearStateProgram will execute in that
# case, not the ApprovalProgram.
def approval_program():
    # Global State Keys
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

    handle_creation = Seq([
        App.globalPut(creator_key, Txn.sender()),  # 1 Bytes
        Assert(Txn.application_args.length() == Int(7)),  # 3 Bytes, 4 Int
        App.globalPut(creator_name_key, Txn.application_args[0]),
        App.globalPut(departure_address_key, Txn.application_args[1]),
        App.globalPut(arrival_address_key, Txn.application_args[2]),
        App.globalPut(departure_date_key, Btoi(Txn.application_args[3])),
        App.globalPut(arrival_date_key, Btoi(Txn.application_args[4])),
        App.globalPut(trip_cost_key, Btoi(Txn.application_args[5])),
        App.globalPut(available_seats_key, Btoi(Txn.application_args[6])),
        Assert(Global.round() <= App.globalGet(departure_date_key)),
        Assert(App.globalGet(departure_date_key) < App.globalGet(arrival_date_key)),
        Assert(App.globalGet(available_seats_key) > Int(0)),
        Return(Int(1))
    ])

    handle_optin = Seq([
        Assert(Global.round() <= App.globalGet(departure_date_key)),
        Assert(App.globalGet(available_seats_key) > Int(0)),
        Return(Int(1))
    ])

    handle_closeout = Seq([
        Return(Int(1))
    ])

    is_creator = Txn.sender() == App.globalGet(creator_key)
    get_participant_state = App.localGetEx(Int(0), App.id(), is_participating_key)

    participant_name = Txn.application_args[1]
    available_seats = App.globalGet(available_seats_key)
    on_participate = Seq(
        Assert(App.globalGet(available_seats_key) > Int(0)),  # check if there is an available seat
        Assert(Global.round() <= App.globalGet(departure_date_key)),  # check if trip is finished
        get_participant_state,
        Assert(
            Or(
                Not(get_participant_state.hasValue()),
                get_participant_state.value() == Int(0)
            )
        ),  # check if already participating
        App.globalPut(available_seats_key, available_seats - Int(1)),
        App.localPut(Int(0), is_participating_key, Int(1)),
        Return(Int(1))
    )

    on_cancel = Seq(
        Assert(Global.round() <= App.globalGet(departure_date_key)),  # check if trip is finished
        get_participant_state,
        Assert(
            And(
                get_participant_state.hasValue(),
                get_participant_state.value() == Int(1)
            )
        ),  # check if not participating
        App.globalPut(available_seats_key, available_seats + Int(1)),
        App.localPut(Int(0), is_participating_key, Int(0)),
        Return(Int(1))
    )

    handle_noop = Seq(
        Assert(Global.group_size() == Int(1)),
        Cond(
            [Txn.application_args[0] == Bytes("participateTrip"), on_participate],
            [Txn.application_args[0] == Bytes("cancelParticipation"), on_cancel]
        )
    )

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )

    return program


def clear_state_program():
    program = Seq([
        Return(Int(1))
    ])

    return program


with open('../carsharing_approval.teal', 'w') as f:
    compiled = compileTeal(approval_program(), Mode.Application, version=5)
    f.write(compiled)

with open('../carsharing_clear_state.teal', 'w') as f:
    compiled = compileTeal(clear_state_program(), Mode.Application, version=5)
    f.write(compiled)
