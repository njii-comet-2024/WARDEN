"""
Transmits rover video to central
Receives control code from central and transmits to arduino

@author [Zoe Rizzo] [@zizz-0]
        [Christopher Prol] [@prolvalone]

Date last modified: 07/11/2024
"""
# Libraries
import cv2 as cv
import pickle
import socket
import numpy as np
import base64
import time
import imutils
import serial
import sys
from gpiozero import Servo
from gpiozero import Motor
from gpiozero import RotaryEncoder
from picamera.array import PiRGBArray
from picamera import PiCamera

# Port locations
RIGHT_TREAD_ONE_FWD = 0
RIGHT_TREAD_ONE_BACK = 0

RIGHT_TREAD_TWO_FWD = 0
RIGHT_TREAD_TWO_BACK = 0

LEFT_TREAD_ONE_FWD = 0
LEFT_TREAD_ONE_BACK = 0

LEFT_TREAD_TWO_FWD = 0
LEFT_TREAD_TWO_BACK = 0

RIGHT_WHEG_FWD = 0
RIGHT_WHEG_BACK = 0

LEFT_WHEG_FWD = 0
LEFT_WHEG_BACK = 0

# Swivel
CAMERA_X = 0
CAMERA_Y = 0

# Telescoping
CAMERA_UP = 0
CAMERA_DOWN = 0

CAMERA = 0

# Global variables

ROVER_IP = '10.255.0.255' # delete later and use `IP`

IP = '192.168.110.228' # change to rover IP
PORT = 55555

arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Allow some time for the Arduino to reset

# s = socket.socket() # TCP

# Electronics declarations

# Camera swivel
# cameraX = Servo(CAMERA_X)
# cameraY = Servo(CAMERA_Y)
# cameraTelescope = Motor(CAMERA_UP, CAMERA_DOWN) # Camera telecoping

# # Tread drive motors
# leftTreadOne = Motor(LEFT_TREAD_ONE_FWD, LEFT_TREAD_ONE_BACK)
# leftTreadTwo = Motor(LEFT_TREAD_TWO_FWD, LEFT_TREAD_TWO_BACK)
# rightTreadOne = Motor(RIGHT_TREAD_ONE_FWD, RIGHT_TREAD_ONE_BACK)
# rightTreadTwo = Motor(RIGHT_TREAD_TWO_FWD, RIGHT_TREAD_TWO_BACK)

# # Wheg motors
# rightWheg = Motor(RIGHT_WHEG_FWD, RIGHT_WHEG_BACK)
# leftWheg = Motor(LEFT_WHEG_FWD, LEFT_WHEG_BACK)

"""
Class for manipulation Rover Camera
"""
class Camera:
    def __init__(self):
        print("initializing")

    """
    This function recieves rover camera feed
    
    this is probably unnecessary given transmitRoverFeed 
    function
    """
    def getRoverFeed():
        capture = cv.VideoCapture(1) # need origin of camera, 2 potentially works, potentially doesnt
        
        while True:
            isTrue, frame = capture.read()
            cv.imshow('frame', frame)
            if cv.waitKey(20) & 0xFF ==ord('q'):
                break

        capture.release()

    """
    Transmits Rover Video Data from a usb camera Over UDP sockets, acting as the server
    """
    def transmitUSBCamFeed():
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
        
    """
    Transmits camera feed from PICAMERA to Central via UDP sockets
    """
    def transmitPiCamFeed():
        bufferSize = 65536
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        hostName = socket.gethostname()
        hostIp = '192.168.110.255'# socket.gethostbyname(hostName)
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

                encoded, buffer = cv.imencode('.jpg', image, [cv.IMWRITE_JPEG_QUALITY, 80])
                message = base64.b64encode(buffer)
                
                serverSocket.sendto(message, clientAddr)
                image = cv.putText(image, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv.imshow('TRANSMITTING VIDEO', image)
                key = cv.waitKey(1) & 0xFF
                rawCapture.truncate(0)
                
                if key == ord('q'):
                    serverSocket.close()
                    camera.close()
                    cv.destroyAllWindows()
                    print('Server stopped by user')
                    exit(0)
                
                if cnt == framesToCount:
                    fps = round(framesToCount / (time.time() - st))
                    st = time.time()
                    cnt = 0
                
                cnt += 1

"""
Class that defines a rover and its functionality
"""
class Rover:
    """
    Initializes an instance of Rover 
    """
    def __init__(self):
        self.loopCount = 0
        self.control = 0 # control state -- even => central, odd => drone
        self.on = True # Rover running

        # UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((IP, PORT))

        # TCP
        # s.connect((CENTRAL_IP, port))

    """
    Starts the rover and runs the drive loop
    @param `maxLoopCount` : how many loops to wait through in the event of an extended period of no controls transmitted
    """
    def start(self, maxLoopCount=1):
        print("Starting rover...")

        while self.on:
            self.drive()
            # If no commands are sent for an extended period of time
            if(self.loopCount > maxLoopCount):
                self.on = False

    """
    Main drive loop
    Will receive controller input from central and transmit to arduino
    """
    def drive(self):
        while self.on:
            serializedControls, addr = self.sock.recvfrom(1024)
            controls = pickle.loads(serializedControls)

            inputCtrls = ",".join(f"{key}:{value}" for key, value in controls.items())
            arduino.write(inputCtrls.encode())
            print("Sent to Arduino: ", inputCtrls)

rover = Rover()
rover.start()