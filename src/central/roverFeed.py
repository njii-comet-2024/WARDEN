"""
connects to rover and recieves camera locations and video feed over UDP 
sockets

@author [Christopher Prol]  [@prolvalone]

Date last modified: 07/30/2024
"""

# Libraries
import socket
import cv2 as cv
import numpy as np 
import base64

ROVER_IP = '192.168.110.78'

"""
This is a class for video reception
"""

class videoReciever:
    def __init__(self):
        print("initializing")

   
    """
    This function recieves Rover Cam footage from the PI Camera.  USE THIS ONE, NOT THE TOP ONE  
    """
    def receiveCamFeed():
        bufferSize = 65536
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        hostName = socket.gethostname()
        hostIp = socket.gethostbyname(hostName)
        print(hostIp)
        port = 9999
        socketAddress = (hostIp, port)
        serverSocket.bind(socketAddress)
        print('Listening at:', socketAddress)
        
        while True:
            
            #msg, clientAddr = serverSocket.recvfrom(bufferSize)
            #print('GOT connection from ', clientAddr)
            WIDTH = 1080
            HEIGHT = 400
            #while vid.isOpened():
            #recieve Packet
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
videoReciever.receiveCamFeed()