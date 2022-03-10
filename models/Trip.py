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

    globalState = None
    creator = None
    creatorName = None
    departureAddress = None
    arrivalAddress = None
    startDate = None
    endDate = None
    availableSeats = 0
    cost = 0
    participants = []

    def __init__(self, tripGlobalState):
        self.globalState = tripGlobalState
        self.creator = tripGlobalState[self.CREATOR_FIELD]
        self.creatorName = tripGlobalState[self.CREATOR_NAME_FIELD]
        self.departureAddress = tripGlobalState[self.DEPARTURE_ADDRESS_FIELD]
        self.arrivalAddress = tripGlobalState[self.ARRIVAL_ADDRESS_FIELD]
        self.startDate = tripGlobalState[self.DEPARTURE_DATE_FIELD]
        self.endDate = tripGlobalState[self.ARRIVAL_DATE_FIELD]
        self.availableSeats = tripGlobalState[self.AVAILABLE_SEATS_FIELD]
        self.cost = tripGlobalState[self.TRIP_COST_FIELD]

        # read participants, exclude used fields
        self.participants = []
        fields = [self.CREATOR_FIELD, self.CREATOR_NAME_FIELD, self.DEPARTURE_ADDRESS_FIELD, self.ARRIVAL_ADDRESS_FIELD,
                  self.DEPARTURE_DATE_FIELD, self.ARRIVAL_DATE_FIELD, self.AVAILABLE_SEATS_FIELD, self.TRIP_COST_FIELD]
        for key, value in tripGlobalState.items():
            if key not in fields and value == 1:
                self.participants.append(key)
        self.participants = np.array(self.participants)

