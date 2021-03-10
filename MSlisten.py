# CLIENT
import socket
import sys
import pickle
import time
import threading
from Request import getClientRequest, getRequestInfo
from Server import clientServerConnectionOutput
from AgendaManagement import cancelMeetingClient, populateAgenda, updateAttendanceAgenda, verifyIfHost, updateScheduledStatus, roomChangeAgenda

port = 6660
validServerName= False

while validServerName is False:
    try:
        print("Enter Server Host Name:")
        serverName = input() #UNDO COMMENT
        serverIP = socket.gethostbyname(serverName) #'localhost'
        validServerName = True
    except socket.gaierror:
        print('***  Cannot Connect to Server Name '+ serverName +'   ***\n     Please Try Again\n')  #REPLACE -> localhost

clientName = socket.gethostname()
clientIP = socket.gethostbyname(clientName)  #REPLACE-> clientIP = socket.gethostbyname(localhost)
print("Client Computer Name is:  " + clientName)
print("Client Computer IP Address is:  " + clientIP)

try:
    # Create UDP Datagram socket Keyword to use
    client_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_listen_socket.setblocking(False)
    client_listen_socket.bind((clientIP, 6660))
    connectionMsg = [('=> '+ str(clientName) + ' has Connected!'), 'ping!']
    confirmConnection = pickle.dumps(connectionMsg)
    # confirmConnection = pickle.dumps(str(serverName))
    connection = client_send_socket.sendto(confirmConnection, (serverIP, 6666))
except socket.error:
    print('Failed to create socket')
    sys.exit()

def clientListen():
    while 1:
        try:
            data, server = client_listen_socket.recvfrom(1024)
            if data:
                reply = pickle.loads(data)
                print('\n  ~~~   INCOMING MESSAGE FROM ' + str(serverName) + '   ~~~\n') #REPLACE->localhost
                print(reply)
                print('\n')
                if str(reply) == 'Connection Successful':
                    clientServerConnectionOutput()
                else:
                    replyInfo = reply[0]
                    requestNumber = getRequestInfo(str(replyInfo))
                    if requestNumber == 2: # ACCEPT # REJECT
                        if reply[0] == "ACCEPT":
                            updateAttendanceAgenda(reply[1], 'Going')
                        if reply[0] == "REJECT":
                            updateAttendanceAgenda(reply[1], 'Not Going')
                    if requestNumber == 4: # WITHDRAW
                        if verifyIfHost(reply[1]) == False:
                            updateAttendanceAgenda(reply[1], 'Not Going')
                    if requestNumber == 7: # INVITE
                        populateAgenda(reply, clientName)
                    if requestNumber == 5: # ADD
                        updateAttendanceAgenda(reply[1], 'Going')
                    # Handle meeting cancellation below
                    if requestNumber == 3 or requestNumber == 8:  # Message notifying client a meeting has been cancelled.
                        bookingNumber = reply[1]
                        cancelMeetingClient(reply[1])
                    if requestNumber == 9:
                        bookingNumber = reply[1]
                        updateAttendanceAgenda(bookingNumber, 'Going')
                    if requestNumber == 10:
                        if verifyIfHost(reply[1]):
                            updateScheduledStatus(reply[1])
                    if requestNumber == 11:
                        roomChangeAgenda(reply[1], reply[2])


        except socket.error:
            pass

client_listen = threading.Thread(target=clientListen)
client_listen.start()
#client_listen.join()
#client_send.join()


# finally:
#    print('closing socket')
#    client_socket.close()
