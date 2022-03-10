from pyteal import *


# Handle each possible OnCompletion type. We don't have to worry about
# handling ClearState, because the ClearStateProgram will execute in that
# case, not the ApprovalProgram.
def approval_program():
    handle_creation = Seq([
        App.globalPut(Bytes("Creator"), Txn.sender()),  # 1 Bytes
        Assert(Txn.application_args.length() == Int(7)),  # 3 Bytes, 4 Int
        App.globalPut(Bytes("Creator_Name"), Txn.application_args[0]),
        App.globalPut(Bytes("Departure_Address"), Txn.application_args[1]),
        App.globalPut(Bytes("Arrival_Address"), Txn.application_args[2]),
        App.globalPut(Bytes("Departure_Date"), Btoi(Txn.application_args[3])),
        App.globalPut(Bytes("Arrival_Date"), Btoi(Txn.application_args[4])),
        App.globalPut(Bytes("Trip_Cost"), Btoi(Txn.application_args[5])),
        App.globalPut(Bytes("Available_Seats"), Btoi(Txn.application_args[6])),
        Assert(Global.round() <= App.globalGet(Bytes("Departure_Date"))),
        Assert(App.globalGet(Bytes("Departure_Date")) < App.globalGet(Bytes("Arrival_Date"))),
        Assert(App.globalGet(Bytes("Available_Seats")) > Int(0)),
        Return(Int(1))
    ])

    handle_optin = Seq([
        Assert(Global.round() <= App.globalGet(Bytes("Departure_Date"))),
        Assert(App.globalGet(Bytes("Available_Seats")) > Int(0)),
        Return(Int(1))
    ])

    handle_closeout = Seq([
        Return(Int(1))
    ])

    is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))
    get_participant_state = App.localGetEx(Int(0), App.id(), Bytes("is_participating"))

    participant = Txn.application_args[1]
    available_seats = App.globalGet(Bytes("Available_Seats"))
    on_participate = Seq(
        Assert(App.globalGet(Bytes("Available_Seats")) > Int(0)),  # check if there is an available seat
        Assert(Global.round() <= App.globalGet(Bytes("Departure_Date"))),  # check if trip is finished
        get_participant_state,
        Assert(
            Or(
                Not(get_participant_state.hasValue()),
                get_participant_state.value() == Int(0)
            )
        ),  # check if already participating
        App.globalPut(participant, Int(1)),
        App.globalPut(Bytes("Available_Seats"), available_seats - Int(1)),
        App.localPut(Int(0), Bytes("is_participating"), Int(1)),
        Return(Int(1))
    )

    on_cancel = Seq(
        Assert(Global.round() <= App.globalGet(Bytes("Departure_Date"))),  # check if trip is finished
        get_participant_state,
        Assert(
            And(
                get_participant_state.hasValue(),
                get_participant_state.value() == Int(1)
            )
        ),  # check if not participating
        App.globalPut(participant, Int(0)),
        App.globalPut(Bytes("Available_Seats"), available_seats + Int(1)),
        App.localPut(Int(0), Bytes("is_participating"), Int(0)),
        Return(Int(1))
    )

    handle_noop = Seq(
        Assert(Global.group_size() == Int(1)),
        Cond(
            [Txn.application_args[0] == Bytes("Participate"), on_participate],
            [Txn.application_args[0] == Bytes("Cancel"), on_cancel]
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


with open('carsharing_approval.teal', 'w') as f:
    compiled = compileTeal(approval_program(), Mode.Application, version=5)
    f.write(compiled)

with open('carsharing_clear_state.teal', 'w') as f:
    compiled = compileTeal(clear_state_program(), Mode.Application, version=5)
    f.write(compiled)
