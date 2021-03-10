import json
import sys
import pickle
import datetime
import time
import threading
import os
from collections import deque
from string import digits
from Server import Server
from Meetings import createMeetingsDB, saveMeeting, getListOfAttendees, getListOfAllInvites, messageDeque
from AgendaManagement import populateAgenda, filename
from datetime import timedelta
from collections import deque
exceptions = IOError, RuntimeError, ValueError


# Create room db if non-existant
def createRoomsDB():
    try:
        print('Create roomDB here')

        data = {}
        data = {
                "room1": {
                    "booked_meetings": [
                        {
                            "booking_number": "",
                            "date": "",
                            "time": ""
                        }
                    ]
                },
                "room2": {
                    "booked_meetings": [
                        {
                            "booking_number": "",
                            "date": "",
                            "time": ""
                        }
                    ]
                }
        }
        with open('roomDB.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
            outfile.close()
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

def bookRoom(clientName, roomNumber, clientRequest, bookingNumber):

    meetingDate = clientRequest[2]
    meetingTime = clientRequest[3]
    try:
        with open('roomDB.json') as roomFile:
            roomDB = json.load(roomFile)
            roomFile.close()
        with open('roomDB.json', 'w') as roomFile:
            newBooking = dict(booking_number = bookingNumber, date = meetingDate, time = meetingTime)
            roomDB[roomNumber]["booked_meetings"] = [*roomDB[roomNumber]["booked_meetings"], newBooking]
            json.dump(roomDB, roomFile, indent=4)
            roomFile.close()
            return bookingRoomResponse(bookingNumber, 'AVAILABLE', clientRequest, roomNumber)
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

def bookingRoomResponse(bookingNumber, bookingResponse, clientRequests, roomNumber):
    responseMsg = ['RESPONSE', bookingNumber, bookingResponse, roomNumber]
    if str(responseMsg[2]) == "AVAILABLE":
        meetingHost = clientRequests[1]
    responseMESSAGE = pickle.dumps(responseMsg)
    # Save in meetingsDB.json
    #bookingNum = saveMeetings()
    # After approval/booking, send invites to participants here
    # return responseMESSAGE
    return responseMsg
# Given the client's REQUEST date and time, check if room1 already has any booked meetings for that given date & time.
# If not, do the same check for room2. If room1 is available, the function simply returns the string 'R1'.
# It does not need to check for room2 because it does not matter which room is booked.
# If none of the rooms are available, returns "NOT AVAILABLE"

def createBookingNumbersDB():
    try:
        data = {}
        with open("bookingNumbersDB.json", 'w') as outfile:
            json.dump(data, outfile, indent=4)
            outfile.close()
    except exceptions as error:
        print('Exception occured in createBookingNumbersDB')
        sys.exit()

def generateBookingNumber(clientName):
    try:
        if (os.path.isfile("bookingNumbersDB.json") != True):
            createBookingNumbersDB()
        with open("bookingNumbersDB.json") as bookingNumbersFile:
            bookingNumbersInfo = json.load(bookingNumbersFile)
            bookingNumbersFile.close()
        if clientName in bookingNumbersInfo.keys():
            bookingNumbersInfo[clientName] = bookingNumbersInfo[clientName] + 1
        else:
            bookingNumbersInfo[clientName] = 1
        bookingNumber = clientName + str(bookingNumbersInfo[clientName])
        with open("bookingNumbersDB.json", "w") as bookingNumbersFile:
            json.dump(bookingNumbersInfo, bookingNumbersFile, indent = 4)
            bookingNumbersFile.close()
        return bookingNumber
    except:
        print('Exception occured in generateBookingNumber')

def checkRoomAvailability(clientRequest):
    # INVITE MT# DATE TIME TOPIC REQUESTER
    clientName = clientRequest[1]
    date = clientRequest[2].strip()
    time = clientRequest[3].strip()
    invites = clientRequest[5]
    try:
        if (os.path.isfile('roomDB.json') != True):
            print("roomDB doesnt exist and making it here")
            createRoomsDB()
        with open('roomDB.json', 'r') as roomFile:
            roomInfo = json.load(roomFile)
            roomFile.close()
            room1available = False
            room2available = False
            for bookings in roomInfo['room1']['booked_meetings']:
                if date == str(bookings['date']) and time == str(bookings['time']):
                    print('Room 1 already has a booking for this date & time')
                    room1available = False
                    break
                room1available = True
            if room1available:
                #bookingNumber = saveMeeting(clientRequest)
                return(saveMeeting(clientRequest, "room1"))
                #return bookRoom(clientName, "room1", clientRequest, bookingNumber)
            else:
                for bookings in roomInfo['room2']['booked_meetings']:
                    if date == str(bookings['date']) and time == str(bookings['time']):
                        print('Room 2 already has a booking for this date & time')
                        return bookingRoomResponse(clientName, 'NOT AVAILABLE', invites, 'none')
                    room2available = True
        if room2available:
            #bookingNumber = saveMeeting(clientRequest)
            #bookingNumber = clientRequest[1]
            return(saveMeeting(clientRequest, "room2"))
            #return bookRoom(clientName, "room2", clientRequest, bookingNumber)
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()


# CANCEL request
# Deletes meeting from roomDB.json
def cancelMeetingRoomDB(bookingNumber):
    try:
        with open('roomDB.json') as roomFile:
            roomDB = json.load(roomFile)
            roomFile.close()
        with open('roomDB.json', 'w') as roomFile:
            newMeetingsList = []
            found = False
            for meeting in roomDB["room1"]["booked_meetings"]:
                if not meeting["booking_number"] == bookingNumber:
                    newMeetingsList.append(meeting)
                else:
                    found = True
            if found:
                roomDB["room1"]["booked_meetings"] = newMeetingsList
                json.dump(roomDB, roomFile, indent = 4)
            else:
                newMeetingsList = []
                for meeting in roomDB["room2"]["booked_meetings"]:
                    if not meeting["booking_number"] == bookingNumber:  #nick check this line
                        newMeetingsList.append(meeting)
                    else:
                        found = True
                if found ==  False:
                    print('cancelMeetingRoomDB: cannot find meeting in roomDB')
                    json.dump(roomDB, roomFile, indent = 4)
                else:
                    roomDB["room2"]["booked_meetings"] = newMeetingsList
                    json.dump(roomDB, roomFile, indent = 4)
            roomFile.close()
    except:
        print('Exception in cancelMeetingRoomDB')
        roomFile.close()

def getRoomByBookingNumber(bookingNumber):
    try:
        with open('roomDB.json', 'r') as roomFile:
            roomInfo = json.load(roomFile)
            roomFile.close()

        for bookings in roomInfo["room1"]['booked_meetings']:
            if bookings["booking_number"] == bookingNumber:
                return "room1"
        for bookings in roomInfo["room2"]['booked_meetings']:
            if bookings["booking_number"] == bookingNumber:
                return "room2"
        return "Booking does not exist"
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()


def doesBookingNumberExist(bookingNumber, roomNumber, newRoom):
    bookingExists = False
    try:
        with open('roomDB.json', 'r') as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data[roomNumber]["booked_meetings"]:
            if meeting["booking_number"]  == bookingNumber:
                bookingExists = True
                bookingDate = meeting["date"]
                bookingTime = meeting["time"]
                if isOtherRoomFree(newRoom, bookingDate, bookingTime) == True:
                    return bookingExists
                else:
                    bookingExists = False
        if bookingExists == False:
            print('     **   ' + roomNumber +' Does Not Have This Booking Number   **')
        return bookingExists

    except exceptions as error:
        print('* Error in doesBookingNumberExist', repr(error))


def isOtherRoomFree(newRoom, date, time):
    try:
        alternateRoomAvailable = True
        with open('roomDB.json', 'r') as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data[newRoom]["booked_meetings"]:
            if meeting["date"]  == date and  meeting["time"]  == time:
                alternateRoomAvailable = False
                print('     **   Alternate Room '+ newRoom +' Is Not Available   **')
                return alternateRoomAvailable
        return alternateRoomAvailable
    except exceptions as error:
        print('* Error in isOtherRoomFree', repr(error))

def roomChangeDB(meetingNumber, maintenanceRoom, newRoom):
    meetingTime = ""
    meetingDate = ""

    try:
        with open('roomDB.json', 'r') as roomFile:
            roomInfo = json.load(roomFile)
            roomFile.close()
        # Get time and date of current meeting in DB
        for bookings in roomInfo[maintenanceRoom]['booked_meetings']:
            if bookings["booking_number"] == meetingNumber:
                meetingTime = bookings["time"]
                meetingDate = bookings["date"]
                roomInfo[maintenanceRoom]['booked_meetings'].remove(bookings)
        newBooking = dict(booking_number = meetingNumber, date = meetingDate, time = meetingTime)
        roomInfo[newRoom]["booked_meetings"] = [*roomInfo[newRoom]["booked_meetings"], newBooking]
        roomChangeInvites = getListOfAllInvites(meetingNumber)
        roomChangeMessage = []
        roomChangeMessage.insert(0, 'ROOM CHANGE')
        roomChangeMessage.insert(1, meetingNumber)
        roomChangeMessage.insert(2, newRoom)
        for invite in roomChangeInvites:
            messageDeque.appendleft([roomChangeMessage, invite])
        # TODO insert cancel meeting here
        # Include reason as "Room is unavailable"
        with open('roomDB.json', "w") as jsonFile:
            json.dump(roomInfo, jsonFile, indent=4)
            jsonFile.close()
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()
