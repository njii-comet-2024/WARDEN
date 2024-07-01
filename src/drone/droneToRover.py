"""
Transmits control code to rover

@author [Vito Tribuzio] [Snoopy-0]

Date last modified: 06/26/2024
"""

# Libraries
import socket

#dictionary for controls
controls = {
    "rightJoy": 0,
    "leftJoy": 0,
    "rightTrigger": 0,
    "leftTrigger": 0,
    "cameraToggle": 0,
    "controlToggle": 0,
    "cameraTelescope": 0,
    "cameraSwivelLeft": 0,
    "cameraSwivelRight": 0
}

def clientProgram():
    #create socket object
    s = socket.socket()
    #Define port for connection
    port = 56789

    #connect to the server on local computer
    s.connect(('127.0.0.1', port))

    #get input
    message = input(" -> ")

    while message.lower().strip() != 'bye':
        s.send(message.encode()) #send message
        data = s.recv(1024).decode() #recieve response

        print('received from server: ' + data) #recieve response

        message = input(" -> ") #again take input

    #close the connection
    s.close()

clientProgram()