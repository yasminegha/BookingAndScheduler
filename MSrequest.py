# CLIENT
import socket
import sys
import pickle
import time
import threading
from Request import getClientRequest, getRequestInfo
from Server import clientServerConnectionOutput
from AgendaManagement import populateAgenda

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
    connectionMsg = [('=> '+ str(clientName) + ' has Connected!'), 'ping!']
    confirmConnection = pickle.dumps(connectionMsg)
    # confirmConnection = pickle.dumps(str(serverName))
    connection = client_send_socket.sendto(confirmConnection, (serverIP, 6666))
except socket.error:
    print('Failed to create socket')
    sys.exit()


def clientSend():
    while 1:
        try:
            time.sleep(1)
            print('\n')
            MESSAGE = getClientRequest(clientName)
            if MESSAGE==0:
                pass
            else:
                sent = client_send_socket.sendto(MESSAGE, (serverIP, 6666))
                # message = pickle.loads(MESSAGE)
                # print('  ===>   SENDING MESSAGE  ' + str(message) + '   ===>\n')
        except socket.error:
            print('Message to: ' + str(serverName) +' Cannot be Sent (MS.py)') # REPLACE->localhost

client_send = threading.Thread(target=clientSend)
client_send.start()
