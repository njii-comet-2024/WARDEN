"""
Server testing for video transmission

@author [Christopher Prol] [@prolvalone]

Date last modified: 07/16/2024
"""
# This is server code to send video frames over UDP
import cv2 as cv
import socket
import base64
import numpy as np



class Camera: 
    def __init__(self):
        print("initializing")

    """
    Transmits Rover Video Data from a usb camera Over UDP sockets, acting as the server
    """
    def recieveCamFeed():
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

Camera.recieveCamFeed()







