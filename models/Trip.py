import numpy as np


class Trip:

    CREATOR_FIELD = 'Creator'
    CREATOR_NAME_FIELD = 'Creator_Name'
    DEPARTURE_ADDRESS_FIELD = 'Departure_Address'
    ARRIVAL_ADDRESS_FIELD = 'Arrival_Address'
    DEPARTURE_DATE_FIELD = 'Departure_Date'
    ARRIVAL_DATE_FIELD = 'Arrival_Date'
    AVAILABLE_SEATS_FIELD = 'Available_Seats'
    TRIP_COST_FIELD = 'Trip_Cost'

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

