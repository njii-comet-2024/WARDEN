"""
Sets up server for all vehicles to connect to - - - acts as client
@author [Vito Tribuzio][@Snoopy-0]

Date last modified: 07/15/2024
"""
import cv2 as cv
import socket 
import numpy as np
import base64

DRONE_IP = '192.168.110.19'
TOP_HORIZ = -300
TOP_VERT = -340
SIDE_VERT = -370
SIDE_HORIZ = -340

class videoReciever:
    def __init__(self):
        print("initializing")

    #This function recieves Rover Cam footage from the PI Camera.  
    def recieveRoverCam():
        #socket information
        bufferSize = 65536
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        print(DRONE_IP)
        port = 22222                                 # can change based on possible interference, etc
        message = b'Hello'                          # test message
       
        #connect to server socket
        clientSocket.sendto(message, (DRONE_IP,port))

        #loop for displaying video
        while True:
            #recieve Packet
            packet,_ = clientSocket.recvfrom(bufferSize)
            #interpret packet
            cameraPosLength = 4
            cameraPos = packet[:cameraPosLength]
            imgData = packet[4:]
            #decode data
            data = base64.b64decode(imgData, ' /')
            npdata = np.fromstring(data, dtype=np.uint8)
            frame = cv.imdecode(npdata, 1)

            #display video
            cv.imshow('TESTING HUD', frame)

            #exit key
            if cv.waitKey(20) &0xFF == ord('q'):
                cv.destroyAllWindows()
                break

videoReciever.recieveRoverCam(DRONE_IP)