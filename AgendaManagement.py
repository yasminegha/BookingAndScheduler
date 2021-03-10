import socket
import json
import sys
import os

exceptions = IOError, RuntimeError, ValueError
HOST = socket.gethostname()
filename = HOST + ".json"

# Create agenda at beginning of cliet interactions
def createAgenda():
    try:
        data = {}
        data['meetings'] = []
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4)
            outfile.close()
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

# Populate participant agenda with meetings
# Format: ['INVITE', 'HORVITZ3', 'room1', '06/12/2019', '10:00', ' dina']
# def populateAgenda(bookingNum, hosting, date, time, room, topic):
def populateAgenda(reply, requesterName):
    # if verifyBookingNumber(reply[1]) == False:
        isHost = False
        isAttending = "Pending"
        if str(reply[6]) == str(requesterName):
            isHost = True
            isAttending = "Going"
        try:
            if (os.path.isfile(filename) != True):
                print("Creating Personal Agenda...")
                createAgenda()
            if verifyBookingNumber(reply[1]) == False:
                with open(filename, 'r') as meetingFile:
                    meetingDB = json.load(meetingFile)
                    meetingFile.close()
                with open(filename, 'w') as meetingFile:
                    if isHost:
                        newBooking = dict(
                            BookingNumber=reply[1],
                            Hosting=isHost,
                            Date=reply[3],
                            Time=reply[4],
                            Room=reply[2],
                            Attendance=isAttending,
                            Topic=reply[5],
                            Status="Not Scheduled")
                    else:
                        newBooking = dict(
                            BookingNumber=reply[1],
                            Hosting=isHost,
                            Date=reply[3],
                            Time=reply[4],
                            Room=reply[2],
                            Attendance=isAttending,
                            Topic=reply[5])
                    meetingDB["meetings"] = [*meetingDB["meetings"], newBooking]
                    json.dump(meetingDB, meetingFile, indent=4)
                    meetingFile.close()
            else:
                return False
        except exceptions as error:
            print('Currently handling:', repr(error))
            sys.exit()

# Verifies if a meeting is already in your agenda
def verifyBookingNumber(bookingNumber):
    bookingExists = False
    try:
        with open(filename, "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data["meetings"]:
            if meeting["BookingNumber"]  == bookingNumber:
                bookingExists = True
        if bookingExists == False:
            print('     **   Booking Number Invalid or Does Not Exist   **')
        return bookingExists
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

# Verifies if youre a host based on the booking number
def verifyIfHost(bookingNumber):
    isHost = False
    try:
        with open(filename, "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data["meetings"]:
            if meeting["BookingNumber"]  == bookingNumber:
                if meeting["Hosting"]  == True:
                    isHost = True
        return isHost
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

def updateScheduledStatus(bookingNumber):
    try:
        with open(filename, "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data["meetings"]:
            if meeting["BookingNumber"]  == bookingNumber:
                meeting["Status"] = "Scheduled"
        with open(filename, 'w') as meetingFile:
            json.dump(data, meetingFile, indent=4)
            meetingFile.close()
    except:
        print('Exception occured in updateScheduledStatus')

def isCancellable(bookingNumber):
    try:
        with open(filename, "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data["meetings"]:
            if meeting["BookingNumber"]  == bookingNumber:
                if meeting["Status"] == "Not Scheduled":
                    print('     **   Cannot Cancel Meeting That Has Not Yet Been Scheduled, Please Wait Until Invite Period Ends   **')
                    return False
                else:
                    return True
    except:
        print('Exception occured in isCancellable')

# Ensure that when you get the second invite, it is not added to the agenda
def isAlreadyInAgenda(bookingNumber):
    isInAgenda = False
    try:
        with open(filename, "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data["meetings"]:
            if meeting["BookingNumber"]  == bookingNumber:
                isInAgenda = True
        return isInAgenda
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

# TODO make sure host doesnt invite themselves to the meeting

# Checks to see if you have another meeting at the same time
def meetingSameTime(date, time, bookingNumber="bookingNumber"):
    try:
        if (os.path.isfile(filename) != True):
            print("Creating Personal Agenda...")
            createAgenda()
            return False
        with open(filename, "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data["meetings"]:
            if meeting["Date"] == date and meeting["Time"] == time and meeting["Attendance"] == "Going":
                if bookingNumber=="bookingNumber":
                    return True
                else:
                    if meeting["BookingNumber"] != bookingNumber:
                        return True
            else:
                return False
        return False
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

def getMeetingTimeByBookingNumber(bookingNumber):
    try:
        with open(filename, "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
        for meeting in data["meetings"]:
            if meeting["BookingNumber"]  == bookingNumber:
                date = meeting["Date"]
                time = meeting["Time"]
                return (date, time)
    except exceptions as error:
        print('* getMeetingTimeByBookingNumber, Currently handling:', repr(error))


# Change attendance status in personal agenda
def updateAttendanceAgenda(bookingNum, attendance):
    try:
        # Cant accept/reject non-existent meetings
        if verifyBookingNumber(bookingNum) == False: # Make sure bookingNumber exists in agenda
            print("Cannot Find Booking Number.")
            return False
        else:
            with open(filename, "r") as jsonFile:
                data = json.load(jsonFile)
                jsonFile.close()
            for meeting in data["meetings"]:
                if meeting["BookingNumber"]  == bookingNum:
                    print('bookingNum matches')
                    dateMeeting = meeting["Date"]
                    timeMeeting = meeting["Time"]
                    if meetingSameTime(dateMeeting, timeMeeting, bookingNum) == False:
                        meeting["Attendance"] = attendance
                    else:
                        print('in else NICK')
            with open(filename, "w") as jsonFile:
                json.dump(data, jsonFile, indent=4)
                jsonFile.close()
    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

def updateAttendanceAgendaBACKUP(bookingNum, attendance):
    dateMeeting = ""
    timeMeeting = ""
    try:
        # Cant accept/reject non-existent meetings
        if verifyBookingNumber(bookingNum) == False: # Make sure bookingNumber exists in agenda
            print("Cannot ACCEPT/REJECT/WITHDRAW/ADD from a meeting not found in your agenda.")
            return False
        if verifyIfHost(bookingNum) != True:
            with open(filename, "r") as jsonFile:
                data = json.load(jsonFile)
                jsonFile.close()
            if attendance == "Going":
                for meeting in data["meetings"]:
                    if meeting["BookingNumber"]  == bookingNum:
                        dateMeeting = meeting["Date"]
                        timeMeeting = meeting["Time"]
                for meeting in data["meetings"]:
                    if meeting["BookingNumber"]  != bookingNum and meeting["Date"] == dateMeeting and meeting["Time"] == timeMeeting and meeting["Attendance"] == "Going":
                        print("You already have a meeting booked at this time. Please withdraw from other meeting before accepting this one.")
                        return False
            with open(filename, "w") as jsonFile:
                json.dump(data, jsonFile, indent=4)
                jsonFile.close()
        elif verifyIfHost(bookingNum) == True:
            print("You cannot ACCEPT/REJECT/WITHDRAW/ADD from a meeting you are hosting. You can always cancel.")
            return False

    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

# Deletes a meeting from the client's personal agenda
# CANCEL request
def cancelMeetingClient(meetingNumber):
    try:
        with open(filename, 'r') as agendaFile:
            agendaDict = json.load(agendaFile)
            agendaFile.close()
        with open(filename, 'w') as agendaFile:
            newMeetingsList = []
            for meeting in agendaDict["meetings"]:
                if not meeting["BookingNumber"] == meetingNumber:
                    newMeetingsList.append(meeting)
            agendaDict["meetings"] = newMeetingsList
            json.dump(agendaDict, agendaFile, indent=4)
            agendaFile.close()
    except:
        print('Error in cancelMeetingClient')

# TODO use this somewhere
# Room change in personal client agenda
def roomChangeAgenda(bookingNum, newRoomNum):
    try:
        print('ROOM CHANGE for MT# ' + bookingNum + " into NEW_ROOM# " + newRoomNum)

        with open(filename, "r") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()

        for meeting in data["meetings"]:
            if meeting["BookingNumber"]  == bookingNum:
                meeting["Room"] = newRoomNum

        with open(filename, "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)
            jsonFile.close()

    except exceptions as error:
        print('Currently handling:', repr(error))
        sys.exit()

def getClientAttendance(bookingNumber):
    try:
        with open(filename, "r") as jsonFile:
                data = json.load(jsonFile)
                jsonFile.close()
        for meeting in data["meetings"]:
            if meeting["BookingNumber"]  == str(bookingNumber):
                meetingAttendance = meeting["Attendance"]
                return meetingAttendance
    except exceptions as error:
        print('*getClientAttendance, Currently handling:', repr(error))
        sys.exit()


def getMeetingInfo(bookingNumber):
    try:
        with open(filename, "r") as jsonFile:
                data = json.load(jsonFile)
                jsonFile.close()
        for meeting in data["meetings"]:
            if meeting["BookingNumber"]  == str(bookingNumber):
                print('here2')
                date = meeting["Date"]
                time = meeting["Time"]
                topic = meeting["Topic"]
                room = meeting["Room"]
                meetingInfo = []
                meetingInfo.insert(0, date)
                meetingInfo.insert(1, time)
                meetingInfo.insert(2, room)
                meetingInfo.insert(3, topic)
                print(meetingInfo)
                return meetingInfo

    except exceptions as error:
            print('Currently handling:', repr(error))
            sys.exit()
