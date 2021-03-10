# SERVER
import socket
import sys
import pickle
import threading
import time
from Request import getRequestInfo, getServerRequest
from Meetings import sendInvites, updateAttendanceMeetings, verifyMeetingAttendance, cancelMeetingServer, messageDeque, getHostByBookingNumber, sendWithdrawReInvited
from RoomManagement import checkRoomAvailability, roomChangeDB, doesBookingNumberExist
from collections import deque
# https://docs.python.org/3.7/tutorial/datastructures.html
PORT = 660
localhost = 'localhost'

try:
    server_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # SOCK_DGRAM specifies datagram (udp) sockets
    server_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    HOST = socket.gethostname()
    IP = socket.gethostbyname(HOST)
    print("Server Computer Name is:  " + HOST)
    print("Server Computer IP Address is:  " + IP)
    server_listen_socket.setblocking(False)
    server_listen_socket.bind((IP, 6666))
    # socket_server.bind((HOST, PORT))
    print('UDP Server Up & Listening\n\n')

except socket.error:
    print('Failed to create socket')
    print(socket.error)
    sys.exit()


def serverSend():
    while 1:
        while messageDeque:
            message = messageDeque.pop()
            if message[1] is not None:
                try:
                    sent = server_send_socket.sendto(pickle.dumps(message[0]), (message[1], 6660))
                    print('  ===>   SENDING MESSAGE  ' + str(message[0]) + ' TO  ' + str(message[1]) + '   ===>\n')
                except socket.error:
                    # print(socket.error)
                    print('Message to: ' + str(message[1]) +' Cannot be Sent (MBMS.py)')


def serverListen():
    while 1:
        try:
            dataAddressBytes = server_listen_socket.recvfrom(1024)
            data = dataAddressBytes[0]
            address = dataAddressBytes[1]
            if data:
                clientName = socket.gethostbyaddr(address[0])
                clientData = pickle.loads(data)
                print('\n  ~~~   INCOMING REQUEST FROM ' + str(clientName[0]) + '   ~~~\n')
                if str(clientData[1]) == ('ping!'):
                    print(str(clientData[0]))
                    connectionMESSAGE = []
                    connectionStr = 'Connection Successful'
                    connectionMESSAGE.insert(0, connectionStr)
                    connectionMESSAGE.insert(1, address[0])
                    messageDeque.appendleft([connectionStr, clientName[0]])
                    # sent = server_send_socket.sendto(pickle.dumps('Connection Successful'), (address[0], 6660))
                    # print(' =>   Sent {} bytes back to {}'.format(sent, address[0]))
                else:
                    print(clientData)
                    print('\n')
                    requestType = str(clientData[0])
                    # request = Request(requestType)
                    requestNumber = getRequestInfo(requestType)
                    if requestNumber == 1:
                        responseMESSAGE = checkRoomAvailability(clientData)
                        roomNumber = responseMESSAGE[3]
                        responseMESSAGE.pop(3)
                        messageDeque.appendleft([responseMESSAGE, address[0]])
                        if str(responseMESSAGE[2]) == "AVAILABLE":
                            bookingNumber = responseMESSAGE[1]
                            sendInvites(bookingNumber, clientData, roomNumber)
                            threading.Timer(20, sendInvites, args=[bookingNumber,  clientData, roomNumber]).start()
                            threading.Timer(35, verifyMeetingAttendance, args=[bookingNumber, roomNumber, clientData[2], clientData[3], clientData[1], clientData[6]]).start()
                    if requestNumber == 2 or requestNumber == 4 or requestNumber == 5:
                        #if requestNumber == 2 or requestNumber == 5:
                        #    meetingCancelled = doesBookingNumberExist(clientData[2])
                        #    if meetingCancelled == False:
                        #        meetingCancelledMessage = ['CANCEL', clientData[2], 'This Meeting Was Canceled']
                        #       messageDeque.appendleft([meetingCancelledMessage, clientData[1]])
                        #        pass
                        if clientData[0]=='ACCEPT':
                            updateAttendanceMeetings(clientData[2], 'true', clientData[1])
                            acceptMessage = ['ACCEPT', clientData[2]]
                            messageDeque.appendleft([acceptMessage, clientData[1]])
                            # else: #mtg not found in meetingsDB, cancel from personal agenda
                            #     cancelMessage = ['CANCEL', clientData[2], 'Meeting was Cancelled by the Host.']
                            #     messageDeque.appendleft([cancelMessage, clientData[1]])
                        if clientData[0] == 'REJECT':
                            updateAttendanceMeetings(clientData[2], 'false', clientData[1])
                            rejectMessage = ['REJECT', clientData[2]]
                            messageDeque.appendleft([rejectMessage, clientData[1]])
                        if clientData[0] == 'ADD':
                            updateAttendanceMeetings(clientData[2], 'true', clientData[1])
                            acceptMessage = ['ADD', clientData[2]]
                            messageDeque.appendleft([acceptMessage, clientData[1]])
                        if clientData[0]=='WITHDRAW':
                            withdrawResend = updateAttendanceMeetings(clientData[3], 'false', clientData[1], True)
                            meetingInfo = [] #[0]date [1]time [2]room [3]topic
                            meetingInfo = clientData[2]
                            bookingNumber = clientData[3]
                            bookingHost = getHostByBookingNumber(bookingNumber)
                            withdrawClientMessage = ['WITHDRAW', bookingNumber]
                            withdrawServerMessage = ['WITHDRAW', bookingNumber, clientData[1]]
                            messageDeque.appendleft([withdrawClientMessage, clientData[1]])
                            messageDeque.appendleft([withdrawServerMessage, bookingHost])
                            if withdrawResend == False:
                                sendWithdrawReInvited(bookingNumber, clientData[2], clientData[1], bookingHost)
                                threading.Timer(30, verifyMeetingAttendance, args=[bookingNumber, meetingInfo[3],  meetingInfo[0], meetingInfo[1], bookingHost, meetingInfo[2], True]).start()
                    elif requestNumber == 3:    # CANCEL
                        print('REQUEST TYPE: ' + str(requestType) + ' request#: ' + str(requestNumber))
                        cancelMeetingServer(clientData[2], clientData[1])
                    if requestNumber == 11:      # ROOM CHANGE
                        roomChangeDB(clientData[1], clientData[2], clientData[3])
                    else:
                        pass
            else:
                pass
        except (socket.error, KeyboardInterrupt):
            pass


server_listen = threading.Thread(target=serverListen)
server_send = threading.Thread(target=serverSend)
server_listen.start()
server_send.start()
