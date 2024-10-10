"""
Connects to rover and receives camera locations and video feed over UDP sockets
Runs on Central Raspberry Pi

@author [Christopher Prol]  [@prolvalone]

Date last modified: 08/05/2024
"""

# Libraries
import socket
import cv2 as cv
import numpy as np 
import base64


#These are for WARDEN and should be same for EXT since they are static IPS
#RoverCam = 192.168.110.169
#Drone =  192.168.110.228
#Rover  = 192.168.110.19
#Central = 192.168.110.5

IP = '10.255.0.102'
PORT = 9999

"""
This is a class for video reception
"""

class videoReceiver:
    def __init__(self):
        print("initializing")

   
    """
    This function receives Rover Cam footage from the PI Camera.  USE THIS ONE, NOT THE TOP ONE  
    """
    def receiveCamFeed(self):
        bufferSize = 65536
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        socketAddress = (IP, PORT)
        serverSocket.bind(socketAddress)
        print('Listening at:', socketAddress)
        
        while True:
            #receive Packet
            packet,_ = serverSocket.recvfrom(bufferSize)
        
            #decode data
            data = base64.b64decode(packet, ' /')
            npdata = np.frombuffer(data, dtype=np.uint8)
            frame = cv.imdecode(npdata, 1)
            
            cv.imshow('TESTING HUD', frame)
                
            key = cv.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
        serverSocket.close()
        cv.destroyAllWindows()

#serverProgram()
recv = videoReceiver()
recv.receiveCamFeed()