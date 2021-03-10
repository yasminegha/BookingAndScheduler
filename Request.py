import pickle
import json
from AgendaManagement import updateAttendanceAgenda, filename, roomChangeAgenda, isCancellable, verifyIfHost, meetingSameTime, getMeetingInfo, getMeetingTimeByBookingNumber,verifyBookingNumber, getClientAttendance
from RoomManagement import roomChangeDB
import datetime

exceptions = IOError, RuntimeError, ValueError

def getServerRequest():
    serverInput = input('Schedule Room Maintenance: \n')
    requestTypeFromServer = serverInput.upper()
    requestNumber = getRequestInfo(requestTypeFromServer)
    if requestNumber == 6:
        getExpectedFields(requestNumber)
        requestDetails = input()
        serverInput = []
        serverInput = requestDetails.split(',')
        entriesProvided = len(serverInput)
        if verifyEntryNumber(entriesProvided, requestNumber) == False:
            print('     **   Invalid Number of Entries   **')
            return 0
        serverRequestMessage = []
        maintenanceRoom = serverInput[1].strip().strip()
        if maintenanceRoom != "room1" and maintenanceRoom != "room2":
            print('     **   Invalid Room   **')
            return 0
        newRoom=""
        if maintenanceRoom == "room1":
            newRoom = "room2"
        if maintenanceRoom == "room2":
            newRoom = "room1"
        serverMessage = []
        serverMessage.insert(0, 'ROOM CHANGE')
        serverMessage.insert(1, serverInput[0])
        serverMessage.insert(2, maintenanceRoom)
        serverMessage.insert(3, newRoom)
        return serverMessage
    elif requestNumber == 0:
            print('     **   Invalid Request Type   **')
            return 0
    else:
        return 0


def getClientRequest(clientName):
    # Collecting Client Request Information
    clientInput = input('Enter a Request Key Word:')
    requestTypeFromClient = clientInput.upper()
    requestNumber = getRequestInfo(requestTypeFromClient)
    getExpectedFields(requestNumber)
    # If the clients request is invalid, requestNumber will be 0
    # If requestNumber is 0, leave function
    if requestNumber == 0:
        print('     **   Invalid Request Type   **')
        return 0
    requestDetails = input()
    msg = []
    msg = requestDetails.split(',')
    entriesProvided = len(msg)
    # If the sufficient entries were not met, leave function
    if verifyEntryNumber(entriesProvided, requestNumber) == False:
        print('     **   Invalid Number of Entries   **')
        getClientRequest(clientName)
        return 0
    addAgendaInfo = False
    if requestNumber == 1:
        msg[2]=msg[2].replace(" ","")
        msg[1]=msg[1].replace(" ","")
        msg[0]=msg[0].replace(" ","")
        #validDate = verifyDate(msg[0], msg[1])
        if verifyDate(msg[0], msg[1]) == True:
            if meetingSameTime(msg[0], msg[1]) == False:
                if verifyMinParticipants(msg) == True:
                    print('')
                else:
                    return 0
            else:
                print('     **   You Are Already Attending A Meeting At This Time   **')
                return 0
        else:
            return 0
    # ACCEPT REJECT OR WITHDRAW
    if requestNumber == 2 or requestNumber ==4:
        bookingNumber = requestDetails
        # Verify if Booking Number is Valid
        if verifyBookingNumber(bookingNumber) == False:
            return 0
        # Verify If Hosting
        else:
            if verifyIfHost(bookingNumber) == True:
                print('     **   Cannot Add Yourself To Meeting You Are Hosting   **')
                return 0
            elif (requestTypeFromClient == 'ACCEPT'):
                # Verify Not Already Going
                print(getClientAttendance(bookingNumber))
                if getClientAttendance(bookingNumber) == "Going":
                    print('     **   You Are Already Attending This Meeting   **')
                    return 0
                elif getClientAttendance(bookingNumber) == "Not Going":
                    print('     **   You Must Add Yourself To Meetings You Have Previously Rejected/Withdrew From   **')
                    return 0
                else:# Verify no Date/Time Overlap
                    (date, time) = getMeetingTimeByBookingNumber(bookingNumber)
                    if meetingSameTime(date,time, bookingNumber) == True:
                        print('     **   You Are Already Attending Another Meeting At This Time  **')
                        return 0
            elif (requestTypeFromClient == 'REJECT'):
                # Verify Not Already Not Going
                if getClientAttendance(bookingNumber) == "Not Going":
                    print('     **   You Are Already Not Attending This Meeting   **')
                    return 0
            elif(requestTypeFromClient == 'WITHDRAW'):
                if getClientAttendance(bookingNumber) == "Not Going":
                    print('     **   You Are Already Not Attending This Meeting   **')
                    return 0
                elif getClientAttendance(bookingNumber) == "Pending":
                    print('     **   You Must Accept A Meeting Invitation Before Withdrawing   **')
                    return 0
                else:
                    agendaInfo = getMeetingInfo(bookingNumber)
                    addAgendaInfo = True
    # CANCEL
    if requestNumber == 3:
        bookingNumber = requestDetails
        if verifyBookingNumber(bookingNumber) == False:
            return 0
        else:
            if verifyIfHost(bookingNumber) == False:
                print('     **   Cannot Cancel A Meeting You Are Not Hosting   **')
                return 0
            if isCancellable(bookingNumber) == False:
                return 0
    # TODO if # of participants drops below minimum, you need to do the stuff in project description
    # ADD
    if requestNumber == 5:
        bookingNumber = requestDetails
        if verifyBookingNumber(bookingNumber) == False:
            return 0
        else:
            if verifyIfHost(bookingNumber) == True:
                print('     **   Cannot Add Yourself To A Meeting You Are Hosting   **')
                return 0
            else:
                if getClientAttendance(bookingNumber) == "Going":
                    print('     **   You Are Already Attending This Meeting   **')
                    return 0
                elif getClientAttendance(bookingNumber) == "Pending":
                    print('     **   You Can Only Add Yourself To A Meeting That You Previously Rejected/Withdrew From   **')
                    return 0
                else:
                    (date, time) = getMeetingTimeByBookingNumber(bookingNumber)
                    if meetingSameTime(date, time, bookingNumber) == True:
                        print('     **   You Are Already Attending Another Meeting At This Time  **')
                        return 0
    if requestNumber == 6:
        msg[1]=msg[1].replace(" ","")
        msg[0]=msg[0].replace(" ","")
        # TODO FIX
        if roomChangeDB(msg[0], msg[1]) != False:
            roomChangeAgenda(msg[0], msg[1])

    # print(requestTypeFromClient)
    # Packaging Client inputs to a single message
    msg.insert(0, requestTypeFromClient)
    msg.insert(1, clientName)
    if addAgendaInfo == True:
        msg.insert(2, agendaInfo)
    print(msg)
    MESSAGE = pickle.dumps(msg)

    return MESSAGE

# Search local agenda to see if we are hosting
# returns True if a client is a host of a meeting, False if not the host or no meeting
def validateHost(bookingNumber):
    validBookingNumber = False
    try:
        with open(filename) as meetingFile:
            meetingDB = json.load(meetingFile)
            for meeting in meetingDB["meetings"]:
                if (meeting["BookingNumber"] == bookingNumber):
                    validBookingNumber = True
                    if (meeting["Hosting"] == True):
                        return True
                    else:
                        print('     **   Must Be the Meeting Host to Cancel a Meeting   **')
                        return False
            if validBookingNumber == False:
                print('     **   Booking Number Does Not Exist   **')
                return False
            meetingFile.close()
    except exceptions as error:
        print('Exception occured in validateHost')
        print(error)
        return False

def getRequestInfo(requestType):
    options = {
        'REQUEST': 1,
        'ACCEPT': 2,
        'REJECT': 2,
        'CANCEL': 3,
        'WITHDRAW': 4,
        'ADD': 5,
        'MAINTENANCE': 6,
        'INVITE': 7,
        'NOT SCHEDULED': 8,
        'ADDED': 9,
        'SCHEDULED': 10,
        'ROOM CHANGE': 11
    }
    if requestType in options:
        requestTypeNumber = int(options.get(requestType))
    else:
        requestTypeNumber = 0
    return requestTypeNumber


def getExpectedFields(requestTypeNumber):
    fields = {
        1: "For REQUEST: Enter [DATE, TIME, MIN # OF PARTICIPANTS, LIST OF PARTICIPANTS, TOPIC]",
        2: "For ACCEPT/REJECT: Enter Meeting #: ",
        3: "For CANCEL: Enter Meeting #",
        4: "For WITHDRAW: Enter Meeting #",
        5: "For ADD: Enter Meeting #",
        6: "For MAINTENANCE: Enter [MT#, MAINTENANCE ROOM#]"
    }
    if requestTypeNumber in fields:
        expectingFields = fields.get(requestTypeNumber)
        print(expectingFields)
    else:
        expectingFields = 0
    return requestTypeNumber
# Checking if sufficient entries were provided based on the request


def verifyEntryNumber(numberOfEntries, requestNum):
    if requestNum == 1 and numberOfEntries == 5:
        print("Request# : " + str(requestNum) + '   Number of Entries Received: ' + str(numberOfEntries))
        # CHECK IF msg[2] (MIN # OF PARTICIPANTS) IS LESS THAN THE NUMBER OF PARTICIPANTS msg[3]
        return True
    elif requestNum == 2 and numberOfEntries == 1:
        print("Request# : " + str(requestNum) + '   Number of Entries Received: ' + str(numberOfEntries))
        return True
    elif (requestNum == 2 or requestNum == 3 or requestNum == 4 or requestNum == 5) and numberOfEntries is 1:
        print("Request# : " + str(requestNum) + '   Number of Entries Received: ' + str(numberOfEntries))
        return True
    elif requestNum == 6 and numberOfEntries is 2:
        print("Request# : " + str(requestNum) + '   Number of Entries Received: ' + str(numberOfEntries))
        return True
    else:
        return False


def verifyMinParticipants(msg):
    minNumParticipants = msg[2]
    listOfParticipants = msg[3].split(' ')
    for participant in listOfParticipants:
        if participant == '':
            listOfParticipants.remove(participant)
    participantsProvied = len(listOfParticipants)
    if int(minNumParticipants) > int(participantsProvied):
        print('     **   The Minimum # of Participants was Not Provided   **')
        return False
    else:
        return True

def verifyMinNumber(minimumNumber):
    try:
        minNum = int(minimumNumber)
        if minNum < 1 or minNum > 9:
            if minNum<0:
                print('     **   Minimum Number of Participants must be a Positive Integer > 0     **   ')
            if minNum>9:
                print('     **   Minimum Number of Participants must be 9 or less to meet Room Capacity     **   ')
            return False
        else:
            return True
    except ValueError:
        print('     **   Invalid Minimum Number of Participants     **   ')
        return False


def verifyDate(dateInput, timeInput):
     try:
        bookingTime = datetime.datetime.strptime(timeInput, '%H:%M')
        time = datetime.datetime.now().strftime('%H:%M')
        currentTime = datetime.datetime.strptime(time, '%H:%M')
        correctDate = datetime.datetime.strptime(dateInput, '%d/%m/%Y').date()
        today = datetime.datetime.strptime(dateInput, '%d/%m/%Y').today().date()
        margin = datetime.timedelta(days = 7)
        if (today <= correctDate):
            if (correctDate <= today + margin):
                if(correctDate != today):
                    return verifyTime(timeInput)
                else:
                    if(bookingTime >= currentTime):
                        return verifyTime(timeInput)
                    else:
                        print("     **   Cannot Make Bookings in the Past (Time)      **   ")
            else:
                print("     **   Cannot Make Bookings More Than 7 Days Ahead of Time      **   ")
                return False
        else:
            print("     **   Cannot Make Bookings in the Past (Date)      **   ")
            return False
     except ValueError:
        # raise ValueError("Incorrect data format, should be DD/MM/YY")
        print("     **   Incorrect Date Format, should be DD/MM/YYYY     **   ")
        return False


def verifyTime(timeInput):
    try:
        bookingTime = datetime.datetime.strptime(timeInput, '%H:%M')
        time = datetime.datetime.now().strftime('%H:%M')
        currentTime = datetime.datetime.strptime(time, '%H:%M')
        openingTime= datetime.datetime.strptime('09:00', '%H:%M')
        closingTime= datetime.datetime.strptime('17:00', '%H:%M')
        if(int(bookingTime.minute) == 00):
            if( openingTime <= bookingTime < closingTime):
                return True
            else:
                print("     **   Incorrect Time, Meeting Rooms are Available from 09:00 to 17:00     **   ")
                return False
        else:
            print("     **   Incorrect Time, Can Only Book Meetings on the Hour     **   ")
            return False
    except ValueError:
       # raise ValueError("Incorrect data format, should be DD/MM/YY")
       print("     **   Incorrect Time Format, should be HH:MM (24-Hour)     **   ")
       return False

'''
class Request:

    def __init__(self, requestType):
        self.requestType = requestType

    def getRequestType(self, requestType):
        self.requestType = getRequestInfo(requestType)
        return self.requestType

    # def addRequest(self, request):
    #    self.requests.append(request)
'''
