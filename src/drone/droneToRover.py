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
    port = 54423

    #connect to the server on local computer
    s.connect(('10.255.0.140', port))

    while True:
        #recieve message from server and print
        message = s.recv(1024).decode()
        print("From server: " + message)

        #if certain message is sent, terminate program
        if message == 'endClient':
            break

    #close the connection
    s.close()

clientProgram()