import json
import sys
import datetime
import time
import threading
import os
from string import digits
from datetime import timedelta
from collections import deque
import AgendaManagement
import RoomManagement
exceptions = IOError, RuntimeError, ValueError

global messageDeque
messageDeque = deque()

# Create meeting db if non-existant
def createMeetingsDB():
    try:
        print('Create meetingsDB here')

        data = {}
        with open('meetingsDB.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
            outfile.close()
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

# Extracts info from client request and adds to meetingsDB
def saveMeeting(clientData,roomStr):
    # clientData is array of 7 request parameters
    # roomStr is the room in which the meeting is to be booked
    # clientName is name of client who requested meeting
    clientName = clientData[1]
    bookingNumber = RoomManagement.generateBookingNumber(clientName)
    try:
        if (os.path.isfile('meetingsDB.json') != True):
            print("Meetings.DB doesnt exist and making it here")
            createMeetingsDB()
        with open('meetingsDB.json', 'r') as meetingsFile:
            meetingsInfo = json.load(meetingsFile)
            # Create New Meeting Object
            newMeeting = {
                "booking_number": bookingNumber,
                "min_attendees": int(clientData[4].strip()),
                "confirmations": 0,
                "invites": []
            }
            invitees = clientData[5].split()
            for ip in invitees:
                invite = {
                    "client_ip": ip,
                    "attending": "pending"
                }
                newMeeting["invites"] = [*newMeeting["invites"], invite]
            meetingsFile.close()
    except:
        print('Exception occured in Save Meetings function')
        meetingsFile.close()
    try:
        with open('meetingsDB.json', 'r') as meetingsFile:
            meetingsInfo = json.load(meetingsFile)
            meetingsFile.close()
        with open('meetingsDB.json', 'w') as meetingsFile:
            booked = False
            for host in meetingsInfo:
                if(host == clientName): # if the host client already has a room booked
                    meetingsInfo[host]["booked_meetings"] = [*meetingsInfo[host]["booked_meetings"], newMeeting]
                    json.dump(meetingsInfo, meetingsFile, indent=4)
                    booked = True
                    break
            if (not booked):
                newClient = {
                    clientName: {
                        "booked_meetings": [
                            newMeeting
                        ],
                    }
                }
                meetingsInfo[clientName] = newClient[clientName]
                json.dump(meetingsInfo, meetingsFile, indent=4)
            meetingsFile.close()
    except:
        print('Error Occured In Save Meetings function')
    return RoomManagement.bookRoom(clientName, roomStr, clientData, bookingNumber)
    #return bookingNumber

# Deletes a meeting from the meetingsDB and roomDB in server
# CANCEL request
def cancelMeetingServer(bookingNumber, host):
    listOfAttendees = getListOfAttendees(bookingNumber)
    # Delete the meeting from meetingsDB.json
    RoomManagement.cancelMeetingRoomDB(bookingNumber)
    reason = "Meeting Was Cancelled By Host"
    try:
        with open('meetingsDB.json', 'r') as meetingsFile:
            meetingsInfo = json.load(meetingsFile)
            meetingsFile.close()
        with open('meetingsDB.json', 'w') as meetingsFile:
            # search through clients until we find the one we're looking for
            #   search through clients bookings until we find the booking we looking for
            for client in meetingsInfo.keys():
                if len(meetingsInfo[client]["booked_meetings"]) == 0:
                    del meetingsInfo[client]
                    break
                else:
                    for meeting in meetingsInfo[client]["booked_meetings"]:
                        if meeting["booking_number"] == bookingNumber:
                            meetingsInfo[client]["booked_meetings"].remove(meeting)
            json.dump(meetingsInfo, meetingsFile, indent = 4)
            meetingsFile.close()
            cancelMsg= []
            cancelMsg.insert(0, 'CANCEL')
            cancelMsg.insert(1, bookingNumber)
            cancelMsg.insert(2, reason)
            if listOfAttendees:
                for attendee in listOfAttendees:
                    messageDeque.appendleft([cancelMsg, attendee])
            messageDeque.appendleft([cancelMsg, host])
            with open('meetingsDB.json', "w") as jsonFile:
                json.dump(meetingsInfo, jsonFile, indent=4)
            jsonFile.close()
    except exceptions as error:
        print('Exception occured in cancelMeetingServer')
        print(error)
        meetingsFile.close()

# Verifies if a meeting is already in your agenda
def verifyBookingNumberDB(bookingNumber):
    bookingExists = False
    try:
        with open('meetingsDB.json', "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data:
            for bookings in data[meeting]["booked_meetings"]:
                if bookings["booking_number"] == bookingNumber:
                    bookingExists = True
        return bookingExists
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()


def updateMeetingAttendanceGoing(bookingNumber, attendance, client):
    try:
        if verifyBookingNumberDB(bookingNumber) == False:
            print("THIS SHOULDNT BE PRINTED: Cannot ACCEPT/REJECT/WITHDRAW from a meeting not found in the database.")
            return 0
        if AgendaManagement.verifyIfHost(bookingNumber) == False:
            with open('meetingsDB.json', "r") as jsonFile:
                data = json.load(jsonFile)
                jsonFile.close()
            for meeting in data:
                for bookings in data[meeting]["booked_meetings"]:
                    if str(bookings["booking_number"]) == bookingNumber:
                        for invites in bookings["invites"]:
                            if str(invites["client_ip"]) == client:
                                invites["attending"] = attendance
                                host = meeting
            roomNumber = RoomManagement.getRoomByBookingNumber(bookingNumber)
            confirmAddMessageClient = ['CONFIRM', bookingNumber, roomNumber]
            confirmAddMessageHost =  ['ADDED', bookingNumber, client]
            messageDeque.appendleft([confirmAddMessageHost, host])
            messageDeque.appendleft([confirmAddMessageClient, client])
            with open('meetingsDB.json', "w") as jsonFile:
                json.dump(data, jsonFile, indent=4)
                jsonFile.close()
        elif AgendaManagement.verifyIfHost(bookingNumber) == True:
            # THIS SHOULD NEVER HAPPEN
            print("You cannot ACCEPT/REJECT/WITHDRAW/ADD from a meeting you are hosting in DB.")
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

def updateMeetingAttendanceNotGoing(bookingNumber, attendance, client):
    try:
        if AgendaManagement.verifyIfHost(bookingNumber) == False:
            with open('meetingsDB.json', "r") as jsonFile:
                data = json.load(jsonFile)
                jsonFile.close()
            for meeting in data:
                for bookings in data[meeting]["booked_meetings"]:
                    if str(bookings["booking_number"]) == bookingNumber:
                        for invites in bookings["invites"]:
                            if str(invites["client_ip"]) == client:
                                if invites["attending"] == "true":
                                    bookings["confirmations"] = bookings["confirmations"] - 1
                                invites["attending"] = attendance
                                host = meeting
            confirmAddMessageClient = ['CONFIRM', bookingNumber, roomNumber]
            confirmAddMessageHost =  ['ADDED', bookingNumber, client]
            messageDeque.appendleft([confirmAddMessageHost, host])
            messageDeque.appendleft([confirmAddMessageClient, client])
            with open('meetingsDB.json', "w") as jsonFile:
                json.dump(data, jsonFile, indent=4)
                jsonFile.close()
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

# Change attendance status in meetingsDB
def updateAttendanceMeetings(bookingNumber, attendance, client, withdrawRequest=False):
    confirmations = 0
    minimumAttendees = 0
    try:
        if verifyBookingNumberDB(bookingNumber) == False:
            # THIS SHOULD NEVER HAPPEN
            print("Cannot ACCEPT/REJECT/WITHDRAW from a meeting not found in the database.")
            return 0
        #if AgendaManagement.verifyIfHost(bookingNumber) == False:
        with open('meetingsDB.json', "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data:
            for bookings in data[meeting]["booked_meetings"]:
                minimumAttendees = bookings["min_attendees"]
                if str(bookings["booking_number"]) == bookingNumber:
                    for invites in bookings["invites"]:
                        if str(invites["client_ip"]) == client:
                            # Confirmations # Adjusted Here
                            if (invites["attending"] == "false" or invites["attending"] == "pending") and attendance=="true":
                                #print('incrementing confirmations number by 1')
                                bookings["confirmations"] = bookings["confirmations"] + 1
                                #print('confirmations: '  + str(bookings["confirmations"]))
                            if invites["attending"] == "true" and attendance=="false":
                                bookings["confirmations"] = bookings["confirmations"] - 1
                                #print(str(bookings["confirmations"] - 1))
                                #print(str(bookings["confirmations"]))
                            #print('attendance before change: ' + str(invites["attending"]))
                            invites["attending"] = attendance  # Attendance Status Changed Here
                            #print('attendance after change: ' + str(invites["attending"]))
                            confirmations = bookings["confirmations"]
                            #print('confirmations: ' + str(confirmations))
                            host = meeting
        with open('meetingsDB.json', "w") as jsonFile:
                json.dump(data, jsonFile, indent=4)
                jsonFile.close()
        if withdrawRequest==True:
            # print(str(confirmations) +  ' ? '  + str(minimumAttendees))
            if confirmations < minimumAttendees:
                # print(str(confirmations) + '<' + str(minimumAttendees))
                return False
            else:
                return True
            withdrawMessage = ['WITHDRAW', bookingNumber, client]
            messageDeque.appendleft([withdrawMessage, host])
        #elif AgendaManagement.verifyIfHost(bookingNumber) == True:
        #    print("You cannot ACCEPT/REJECT/WITHDRAW/ADD from a meeting you are hosting in DB.")
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

def verifyMeetingAttendance(bookingNumber, room, date, time, host, topic, withdrawRequest=False):
    #time.sleep(50)
    with open('meetingsDB.json', 'r') as meetingsFile:
        try:
            meetingsInfo = json.load(meetingsFile)
            meetingsFile.close()
        except:
            print('Exception occured in verifyMeetingAttendance')
    for client in meetingsInfo.keys():
        host = client
        for meeting in meetingsInfo[client]["booked_meetings"]:
            if meeting["booking_number"] == bookingNumber:
                if int(meeting["confirmations"]) >= int(meeting["min_attendees"]):
                    #print(str(meeting["confirmations"]) + "  ? " + str(meeting["min_attendees"]))
                    print('Min Participants reached')
                    if withdrawRequest == False:
                        sendScheduled(bookingNumber, room, host) # to meeting host
                        sendConfirmation(bookingNumber, room)  # to invitees
                        break
                else:
                    print('Min Participants not reached')
                    if withdrawRequest == True:
                        sendCancellation(bookingNumber, True) # to Invitees + Host
                        cancelMeetingServer(bookingNumber, host)
                    else:
                        sendNotScheduled(bookingNumber, date, time, host, topic) # to meeting host
                        sendCancellation(bookingNumber) # to invitees
                        cancelMeetingServer(bookingNumber, host)
                        break

    return 0

def getMinByBookingNumber(bookingNumber):
    with open('meetingsDB.json', 'r') as meetingsFile:
        try:
            meetingsInfo = json.load(meetingsFile)
            meetingsFile.close()
        except:
            print('Exception occured in getMinByBookingNumber')
    for client in meetingsInfo.keys():
        for meeting in meetingsInfo[client]["booked_meetings"]:
            if meeting["booking_number"] == bookingNumber:
                return int(meeting["min_attendees"])
    return 0


def getHostByBookingNumber(bookingNumber):
    try:
        with open('meetingsDB.json', "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data:
            for bookings in data[meeting]["booked_meetings"]:
                if str(bookings["booking_number"]) == bookingNumber:
                   return meeting
        return False

    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

def getPendingNotGoing(bookingNumber):
    pendingNotGoing = []
    try:
        with open('meetingsDB.json', "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data:
            for bookings in data[meeting]["booked_meetings"]:
                if str(bookings["booking_number"]) == bookingNumber:
                    for invites in bookings["invites"]:
                        if invites["attending"] ==  "pending" or invites["attending"] ==  "false":
                            pendingNotGoing.append(invites["client_ip"])
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()
    return pendingNotGoing


def getPendingAttendees(bookingNumber):
    pendingAttendeesList = []
    try:
        with open('meetingsDB.json', "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data:
            for bookings in data[meeting]["booked_meetings"]:
                if str(bookings["booking_number"]) == bookingNumber:
                    for invites in bookings["invites"]:
                        if invites["attending"] ==  "pending":
                            pendingAttendeesList.append(invites["client_ip"])
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()
    return pendingAttendeesList

def getListOfAllInvites(bookingNumber):
    try:
        with open('meetingsDB.json', 'r') as meetingsFile:
            meetingsInfo = json.load(meetingsFile)
            meetingsFile.close()
        for client in meetingsInfo.keys():
            for meeting in meetingsInfo[client]["booked_meetings"]:
                invitees = []
                invitees.append(client)
                if meeting["booking_number"] == bookingNumber:
                    for invitee in meeting["invites"]:
                        invitees.append(invitee["client_ip"])
                        return invitees
    except:
        print('** Exception occured in getListOfAllInvites')

def getListOfAttendees(bookingNumber):
    try:
        with open('meetingsDB.json', 'r') as meetingsFile:
            meetingsInfo = json.load(meetingsFile)
            meetingsFile.close()
        for client in meetingsInfo.keys():
            for meeting in meetingsInfo[client]["booked_meetings"]:
                if meeting["booking_number"] == bookingNumber:
                    invitees = []
                    for invitee in meeting["invites"]:
                        if invitee["attending"] == "true":
                            invitees.append(invitee["client_ip"])
                            return invitees
    except:
        print('Exception occured in listOfAttendees')

def sendWithdrawReInvited(bookingNumber, meetingInfo , requester, host):
    bookingHost = getHostByBookingNumber(bookingNumber)
    date = meetingInfo[0]
    time = meetingInfo[1]
    room = meetingInfo[2]
    topic = meetingInfo[3]
    try:
        print('Resending Invites *due to Withdraw*')
        listOfInvites = getPendingNotGoing(bookingNumber)
        if listOfInvites:
            reInviteMessage = ['INVITE', bookingNumber, room, date, time, topic, bookingHost]
            for invitee in listOfInvites:
                messageDeque.appendleft([reInviteMessage, invitee])
    except exceptions as error:
        print('Currently handling:', repr(error))
        print('Error occured in trying to resend invitations due to withdrawal')


# Send invites to list of participants
def sendInvites(bookingNumber, clientRequest, room):
    # INVITE MT# DATE TIME TOPIC REQUESTER
    meetingHost = clientRequest[1]
    meetingDate = clientRequest[2]
    meetingTime = clientRequest[3]
    invitations = clientRequest[5]
    meetingTopic = clientRequest[6]
    try:
        listOfInvites = invitations.split(' ')
        for invite in listOfInvites:
            if invite == ' ' or invite =='' or invite =="":
                listOfInvites.remove(invite)
        listOfInvites.append(meetingHost)
        inviteMessage = []
        inviteMessage.insert(0, 'INVITE')
        inviteMessage.insert(1, bookingNumber)
        inviteMessage.insert(2, room)
        inviteMessage.insert(3, meetingDate)
        inviteMessage.insert(4, meetingTime)
        inviteMessage.insert(5, meetingTopic)
        inviteMessage.insert(6, meetingHost)
        if listOfInvites:
            for invite in listOfInvites:
                messageDeque.appendleft([inviteMessage, invite])
        # We will have to test it at school with unique IPs
        # to make sure the host and all participants get it. And then
        # fix MeetingNumber, RoomNumber and Host

    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()


def sendCancellation(bookingNumber, sendToHost=False):
    try:
        print("Sending Cancellations")
        confirmedParticipants = getListOfAttendees(bookingNumber)
        reason = 'Minimum Participant Requirements Was Not Met'
        cancelMessage = []
        cancelMessage.insert(0, 'CANCEL')
        cancelMessage.insert(1, bookingNumber)
        cancelMessage.insert(2, reason)
        if confirmedParticipants:
            for participant in confirmedParticipants:
                messageDeque.appendleft([cancelMessage, participant])
        if sendToHost == True:
            meetingHost = getHostByBookingNumber(bookingNumber)
            messageDeque.appendleft([cancelMessage, meetingHost])
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

def sendConfirmation(bookingNumber, room, sendToHost=False, host=''):
    try:
        # print('Sending Confirmations')
        confirmedParticipants = getListOfAttendees(bookingNumber)
        confirmMessage = []
        confirmMessage.insert(0, 'CONFIRM')
        confirmMessage.insert(1, bookingNumber)
        confirmMessage.insert(2, room)
        if confirmedParticipants:
            for participant in confirmedParticipants:
                messageDeque.appendleft([confirmMessage, participant])
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()


def sendScheduled(bookingNumber, room, host):
    try:
        # print('Sending Scheduled Confirmation to Host')
        confirmedParticipants = getListOfAttendees(bookingNumber)
        scheduledMessage = []
        scheduledMessage.insert(0, 'SCHEDULED')
        scheduledMessage.insert(1, bookingNumber)
        scheduledMessage.insert(2, room)
        scheduledMessage.insert(3, confirmedParticipants)
        messageDeque.appendleft([scheduledMessage, host])

    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

# sendNotScheduled(bookingNumber, date, time, minimum, host, topic) # to meeting host
def sendNotScheduled(bookingNumber, date, time, host, topic):
    try:
        confirmedParticipants = getListOfAttendees(bookingNumber)
        notScheduledMessage = []
        notScheduledMessage.insert(0, 'NOT SCHEDULED')
        notScheduledMessage.insert(1, bookingNumber)
        notScheduledMessage.insert(2, date)
        notScheduledMessage.insert(3, time)
        minimum = getMinByBookingNumber(bookingNumber)
        notScheduledMessage.insert(4, minimum)
        notScheduledMessage.insert(5, confirmedParticipants)
        notScheduledMessage.insert(6, topic)
        messageDeque.appendleft([notScheduledMessage, host])

    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()
