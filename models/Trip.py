import json
import numpy as np


class Trip:

    CREATOR_FIELD = 'creator'
    CREATOR_NAME_FIELD = 'creator_name'
    DEPARTURE_ADDRESS_FIELD = 'departure_address'
    ARRIVAL_ADDRESS_FIELD = 'arrival_address'
    DEPARTURE_DATE_FIELD = 'departure_date'
    ARRIVAL_DATE_FIELD = 'arrival_date'
    AVAILABLE_SEATS_FIELD = 'available_seats'
    TRIP_COST_FIELD = 'trip_cost'
    PARTICIPANTS_FIELD = 'participants'

    globalState = None
    creator = None
    creatorName = None
    departureAddress = None
    arrivalAddress = None
    startDate = None
    endDate = None
    availableSeats = 0
    cost = 0
    participants = {}

    def __init__(self, tripGlobalState):
        self.globalState = tripGlobalState
        self.creator = tripGlobalState.get(self.CREATOR_FIELD)
        self.creatorName = tripGlobalState.get(self.CREATOR_NAME_FIELD)
        self.departureAddress = tripGlobalState.get(self.DEPARTURE_ADDRESS_FIELD)
        self.arrivalAddress = tripGlobalState.get(self.ARRIVAL_ADDRESS_FIELD)
        self.startDate = tripGlobalState.get(self.DEPARTURE_DATE_FIELD)
        self.endDate = tripGlobalState.get(self.ARRIVAL_DATE_FIELD)
        self.availableSeats = tripGlobalState.get(self.AVAILABLE_SEATS_FIELD)
        self.cost = tripGlobalState.get(self.TRIP_COST_FIELD)

        # read participants, exclude used fields
        self.participants = {}
        if tripGlobalState.get(self.PARTICIPANTS_FIELD) is not None:
            self.participants = json.loads(tripGlobalState.get(self.PARTICIPANTS_FIELD))

    def addParticipant(self, user):
        self.participants.update([(user, 1)])

    def removeParticipant(self, user):
        self.participants.update([(user, 0)])

    def getParticipants(self):
        return json.dumps(self.participants)
