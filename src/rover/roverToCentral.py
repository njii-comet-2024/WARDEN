"""
Transmits rover video to central - - -  acts as server
Receives control code from central and runs on rover

@author [Zoe Rizzo] [@zizz-0]
        [Christopher Prol] [@prolvalone]
        [vito tribuzio] [@Snoopy-0]

Date last modified: 07/16/2024
"""
# Libraries
import cv2 as cv
import pickle
import socket
import base64
import time
import serial
from gpiozero import Motor
from gpiozero import Servo
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# PINS
# IN1 => CLOCKWISE
# IN2 => COUNTER-CLOCKWISE
# Motor 1 -- Right main treads
M1_ENA = 0
M1_IN1 = 0
M1_IN2 = 0

# Motor 2 -- Left main treads
M2_ENA = 0
M2_IN1 = 0
M2_IN2 = 0

# Motor 3 -- Left wheg treads
M3_ENA = 0
M3_IN1 = 0
M3_IN2 = 0

# Motor 4 -- Left wheg treads
M4_ENA = 0
M4_IN1 = 0
M4_IN2 = 0

# Motor 5 -- Right wheg treads (DM456AI)
M5_ENA = 0
M5_OPTO = 0
M5_DIR = 0

# Motor 6 -- Left wheg treads  (DM456AI)
M6_ENA = 0
M6_OPTO = 0
M6_DIR = 0

# Motor 7 -- Camera Telescope Linear Actuator
M7_IN1 = 0
M7_IN2 = 0

stepsPerRevolution = 200; # for steppers == adjust based on steppers

# Servo 1 -- Camera tilt
S1_PIN = 0

# Servo 2 -- Camera swivel
S2_PIN = 0

# Servo 3 -- Camera zoom
S3_PIN = 0

# Tread motors
rightMainTread = Motor(M1_IN1, M1_IN2, M1_ENA)
leftMainTread = Motor(M2_IN1, M2_IN2, M2_ENA)
rightWhegTread = Motor(M3_IN1, M3_IN2, M3_ENA)
leftWhegTread = Motor(M4_IN1, M4_IN2, M4_ENA)

# Camera motor/servos
telescope = Motor(M7_IN1, M7_IN2)
tilt = Servo(S1_PIN)
swivel = Servo(S2_PIN)
zoom = Servo(S3_PIN)

# Global variables
IP = '192.168.110.19'  # change to rover IP
PORT = 55555

cameraType = 0

rightSpeed = 0
leftSpeed = 0

tiltPos = 0
swivelPos = 0
zoomPos = 0
telePos = 0 # change to middle position

"""
State interface used to determine and switch camera state (from regular to IR)
"""
class CameraTypeState:
    _state = 'REG'

    """
    Switches state from reg to IR (and vice versa)
    """
    def switch(self):
        # TODO: add code to switch on microcontroller
        if self._state == 'REG':
            self._state = 'IR'
            print("Camera IR")
        elif self._state == 'IR':
            self._state = 'REG'
            print("Camera REG")
        else:
            pass # incorrect input
    
    """
    Returns the current state
    """
    def getState(self):
        return self._state

"""
Class for manipulation Rover Camera
"""
class Camera:
    def __init__(self):
        print("initializing")

    """
    Maps a number from one range to another
    @param `num` : number to re-map
    @param `inMin` : original range min
    @param `inMax` : original range max
    @param `outMin` : target range min
    @param `outMax` : target range max
    """
    def numToRange(num, inMin, inMax, outMin, outMax):
        return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax
                        - outMin))

    """
    Transmits Rover Video Data from a usb camera Over UDP sockets, acting as the server
    """
    def transmitUSBCamFeed(self):
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

        vid = cv.VideoCapture(0)

        while True:
            # re-maps camera values and converts to bytearray
            newTilt = self.numToRange(tiltPos, -1, 1, 0, 180)
            newSwivel = self.numToRange(swivelPos, -1, 1, 0, 205)
            newTele = self.numToRange(telePos, 0, 1, 0, 180) # figure out actual max
            newZoom = self.numToRange(zoomPos, -1, 1, 0, 10)
            cameraPos = [newTilt, newSwivel, newTele, newZoom]
            cameraPosByte = bytearray(cameraPos)

            msg, clientAddr = serverSocket.recvfrom(bufferSize)
            print('GOT connection from ', clientAddr)
            WIDTH = 400
            HEIGHT = 1080
            while vid.isOpened():
                _, frame = vid.read()
                frame = cv.resize(frame, (WIDTH, HEIGHT))
                encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

                message = base64.b64encode(buffer)
                combined = cameraPosByte + message
                serverSocket.sendto(combined, clientAddr)
                
                cv.imshow('TRANSMITTING VIDEO', frame)
                key = cv.waitKey(1) & 0xFF
                if key == ord('q'):
                    serverSocket.close()
                    break

    """
    Transmits camera feed from Picamera2 to Central via UDP sockets
    """
    def transmitPiCamFeed(self):
        bufferSize = 65536
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        hostName = socket.gethostname()
        hostIp = '192.168.110.255'  # socket.gethostbyname(hostName)
        print(hostIp)
        port = 9999
        socketAddress = (hostIp, port)
        serverSocket.bind(socketAddress)
        print('Listening at:', socketAddress)

        # Initialize Picamera2
        picam2 = Picamera2()
        videoConfig = picam2.create_video_configuration(main={"size": (640, 480)})
        picam2.configure(videoConfig)
        picam2.start()

        while True:
            # re-maps camera values and converts to bytearray
            newTilt = self.numToRange(tiltPos, -1, 1, 0, 180)
            newSwivel = self.numToRange(swivelPos, -1, 1, 0, 205)
            newTele = self.numToRange(telePos, 0, 1, 0, 180) # figure out actual max
            newZoom = self.numToRange(zoomPos, -1, 1, 0, 10)
            cameraPos = [newTilt, newSwivel, newTele, newZoom]
            cameraPosByte = bytearray(cameraPos)

            msg, clientAddr = serverSocket.recvfrom(bufferSize)
            print('GOT connection from ', clientAddr)
            WIDTH = 400
            while True:
                buffer = picam2.capture_array("main")
                frame = cv.cvtColor(buffer, cv.COLOR_RGB2BGR)
                frame = cv.resize(frame, (WIDTH, int(WIDTH * frame.shape[1] / frame.shape[0])), interpolation=cv.INTER_AREA)
                print('Resized frame size:', frame.shape)

                encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

                message = base64.b64encode(buffer)
                combined = cameraPosByte + message
                serverSocket.sendto(combined, clientAddr)
                
                cv.imshow('TRANSMITTING VIDEO', frame)
                key = cv.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    serverSocket.close()
                    picam2.stop()
                    cv.destroyAllWindows()
                    print('Server stopped by user')
                    exit(0)
                
"""
Class that defines a rover and its functionality
"""
class Rover:
    """
    Initializes an instance of Rover 
    """
    def __init__(self):
        self.loopCount = 0
        self.control = 0  # control state -- even => central, odd => drone
        self.on = True  # Rover running
        self.cameraType = CameraTypeState()

        # UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((IP, PORT))
        msg, clientAddr = self.sock.recvfrom(65536)
        print('GOT connection from ', clientAddr)

    """
    Starts the rover and runs the drive loop
    @param `maxLoopCount` : how many loops to wait through in the event of an extended period of no controls transmitted
    """
    def start(self, maxLoopCount=1):
        print("Starting rover...")

        while self.on:
            self.drive()
            # If no commands are sent for an extended period of time
            if self.loopCount > maxLoopCount:
                self.on = False

    """
    Main drive loop
    Will receive controller input from central and transmit to arduino
    """
    def drive(self):
        while self.on:
            ctrls = []
            serializedControls, addr = self.sock.recvfrom(1024)
            controls = pickle.loads(serializedControls)  # unserializes controls

            leftSpeed = abs(controls["leftTread"])
            rightSpeed = abs(controls["rightTread"])

            if(controls["leftTreads"] > 0):
                leftMainTread.forward(leftSpeed)
                leftWhegTread.forward(leftSpeed)
                ctrls.append("Left fwd")

            if(controls["rightTreads"] < 0):
                leftMainTread.backward(leftSpeed)
                leftWhegTread.backward(leftSpeed)
                ctrls.append("Left back")

            if(controls["rightTreads"] > 0):
                rightMainTread.forward(rightSpeed)
                rightWhegTread.forward(rightSpeed)
                ctrls.append("Right fwd")

            if(controls["rightTreads"] < 0):
                rightMainTread.backward(rightSpeed)
                rightWhegTread.backward(rightSpeed)
                ctrls.append("Right back")

            if(controls["leftWheg"] > 0):
                ctrls.append("Left wheg up")

            if(controls["leftWheg"] < 0):
                ctrls.append("Left wheg down")
            
            if(controls["rightWheg"] > 0):
                ctrls.append("Right wheg up")

            if(controls["rightWheg"] < 0):
                ctrls.append("Right wheg down")

            if(controls["cameraTypeToggle"] > 0):
                self.cameraType.switch()
                ctrls.append("Camera switch")

            if(controls["cameraTelescope"] > 0):
                # find max
                # if telePos < max
                telescope.forward()
                telePos += 1
                ctrls.append("Telescope up")
            
            if(controls["cameraTelescope"] < 0):
                if(telePos > 0):
                    telescope.backward()
                    telePos -= 1
                    ctrls.append("Telescope down")

            if(controls["cameraTilt"] > 0):
                if(tiltPos < 1):
                    tiltPos += 0.05
                    tilt.value = tiltPos
                    ctrls.append("Tilt up")
            
            if(controls["cameraTilt"] < 0):
                if(tiltPos > -1):
                    tiltPos -= 0.05
                    tilt.value = tiltPos
                    ctrls.append("Tilt down")

            if(controls["cameraLeft"] > 0):
                if(swivelPos > -1):
                    swivelPos -= 0.05
                    swivel.value = swivelPos
                    ctrls.append("Swivel left")
            
            if(controls["cameraRight"] > 0):
                if(swivelPos < 1):
                    swivelPos += 0.05
                    swivel.value = swivelPos
                    ctrls.append("Swivel right")
            
            if(controls["cameraZoom"] > 0):
                if(zoomPos < 1):
                    zoomPos += 0.5
                    zoom.value = zoomPos
                    ctrls.append("Zoom in")

            if(controls["cameraZoom"] < 0):
                if(zoomPos > -1):
                    zoomPos -= 0.5
                    zoom.value = zoomPos
                    ctrls.append("Zoom out")
            
            if(ctrls):
                print(ctrls)
            


rover = Rover()
rover.start()

# cam = Camera
# cam.transmitUSBCamFeed()
