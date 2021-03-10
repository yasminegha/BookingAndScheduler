# SERVER
import socket
import sys
import pickle
import threading
import time
from RoomManagement import doesBookingNumberExist
from Request import getRequestInfo, getServerRequest, verifyEntryNumber, getExpectedFields
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

except socket.error:
    print('Failed to create socket')
    print(socket.error)
    sys.exit()

def serverSend():
    while 1:
        serverRoomChange()


def serverRoomChange():
    maintenanceMessage = getServerRequest()
    if maintenanceMessage==0:
        pass
    else:
        print(maintenanceMessage)
        bookingNumber = maintenanceMessage[1]
        maintenanceRoom = maintenanceMessage[2]
        if maintenanceRoom == "room1":
            newRoom = "room2"
            print(newRoom)
            if doesBookingNumberExist(bookingNumber, maintenanceRoom, newRoom) == True:
                print('  ===>  SENDING MESSAGE ' + str(maintenanceMessage) + ' TO ' + str(HOST) + '  ===>\n')
                sent = server_send_socket.sendto(pickle.dumps(maintenanceMessage), (HOST, 6666))
        elif maintenanceRoom == "room2":
            newRoom = "room1"
            if doesBookingNumberExist(bookingNumber, maintenanceRoom, newRoom) == True:
                print('  ===>  SENDING MESSAGE ' + str(maintenanceMessage) + ' TO ' + str(HOST) + '  ===>\n')
                sent = server_send_socket.sendto(pickle.dumps(maintenanceMessage), (HOST, 6666))


server_send = threading.Thread(target=serverSend)
server_send.start()

'''
while messageDeque:
message = messageDeque.popleft()
if message[1] is not None:
try:
sent = server_send_socket.sendto(pickle.dumps(message[0]), (message[1], 6660))
print('  ===>   SENDING MESSAGE  ' + str(message[0]) + ' TO  ' + str(message[1]) + '   ===>\n')
    '''
