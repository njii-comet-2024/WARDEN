"""
Transmits rover video to central either directly or through drone
Receives control code from central or drone and runs on rover

@author Zoe Rizzo [@zizz-0]

Date last modified: 07/02/2024
"""
# Libraries
import cv2 as cv
import pickle
import struct
import socket
import numpy as np
import base64
import time
import imutils

# Pin locations
LEFT_JOYSTICK = 0
RIGHT_JOYSTICK = 0

def drive():
    # Main drive loop
    print("vroom")
    
class Camera:
"""
Class for manipulation Rover Camera
"""
    def __init__(self):
        print("initializing")

    def getRoverFeed():
        """
        This function recieves rover camera feed
        
        this is probably unnecessary given transmitRoverFeed 
        function
        """
        capture = cv.VideoCapture(1) # need origin of camera, 2 potentially works, potentially doesnt
        
        while True:
            isTrue, frame = capture.read()
            cv.imshow('frame', frame)
            if cv.waitKey(20) & 0xFF ==ord('q'):
                break

        capture.release()

    def transmitRoverFeed():
        """
        Transmits Rover Video Data Over UDP sockets, acting as the server
        """
        bufferSize = 65536
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        hostName = socket.gethostname()
        hostIp = socket.gethostbyname(hostName)
        print(hostIp)
        port = 9999
        socketAddress = (hostIp,port)
        serverSocket.bind(socketAddress)
        print('Listening at:', socketAddress)

        vid = cv.VideoCapture(1) #  replace 'rocket.mp4' with 0 for webcam
        fps, st, framesToCount, cnt = (0,0,20,0)

        while True:
            msg,clientAddr = serverSocket.recvfrom(bufferSize)
            print('GOT connection from ', clientAddr)
            WIDTH=400
            while(vid.isOpened()):
                _,frame = vid.read()
                frame = imutils.resize(frame,width=WIDTH)
                encoded, buffer = cv.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY,80])
                message = base64.b64encode(buffer)
                serverSocket.sendto(message,clientAddr)
                frame = cv.putText(frame, 'FPS: '+str(fps), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
                cv.imshow('TRANSMITTING VIDEO', frame)
                key = cv.waitKey(1) & 0xFF
                if key == ord('q'):
                    serverSocket.close()
                    break
                if cnt == framesToCount:
                    try:
                        fps = round(framesToCount/(time.time()-st))
                        st=time.time()
                        cnt=0
                    except:
                        pass
                cnt+=1


if __name__ == '__main__':
    drive()
