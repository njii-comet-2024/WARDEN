"""
server testing for video transmission

@author [Christopher Prol] [@prolvalone]

Date last modified: 07/08/2024
"""
# This is server code to send video frames over UDP
import cv2
import imutils
import socket
import numpy as np
import time
import base64
from picamera.array import PiRGBArray
from picamera import PiCamera

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

# Initialize PiCamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

fps, st, framesToCount, cnt = (0, 0, 20, 0)

while True:
    msg, clientAddr = serverSocket.recvfrom(bufferSize)
    print('GOT connection from ', clientAddr)
    WIDTH = 400
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        print('Captured frame size:', image.shape)
        
        image = imutils.resize(image, width=WIDTH)
        print('Resized frame size:', image.shape)

        encoded, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        message = base64.b64encode(buffer)
        
        serverSocket.sendto(message, clientAddr)
        image = cv2.putText(image, 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow('TRANSMITTING VIDEO', image)
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        
        if key == ord('q'):
            serverSocket.close()
            camera.close()
            cv2.destroyAllWindows()
            print('Server stopped by user')
            exit(0)
        
        if cnt == framesToCount:
            fps = round(framesToCount / (time.time() - st))
            st = time.time()
            cnt = 0
        
        cnt += 1

cv2.destroyAllWindows()
