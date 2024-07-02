"""
Transmits rover video to central either directly or through drone
Receives control code from central or drone and runs on rover

@author [Zoe Rizzo] [@zizz-0]
        [Christopher Prol] [prolvalone]

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
from gpiozero import Servo
from gpiozero import Motor
from gpiozero import RotaryEncoder

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

CAMERA_X = 0 # Swivel
CAMERA_ENCODER_ONE = 0
CAMERA_ENCODER_TWO = 0
# Telescoping
CAMERA_Y_FWD = 0
CAMERA_Y_BACK = 0

CAMERA = 0

# Global variables

DRONE_IP = '10.255.0.102'
CENTRAL_IP = '10.255.0.102'

rightSpeed = 0
leftSpeed = 0

s = socket.socket()
port = 56789

# Electronics declarations
# cameraX = Servo(CAMERA_X) # Camera swivel
# cameraEncoder = RotaryEncoder(CAMERA_ENCODER_ONE, CAMERA_ENCODER_TWO, max_steps=10)
# cameraY = Motor(CAMERA_Y_FWD, CAMERA_Y_BACK) # Camera telecoping

# # Tread drive motors
# leftTreadOne = Motor(LEFT_TREAD_ONE_FWD, LEFT_TREAD_ONE_BACK)
# leftTreadTwo = Motor(LEFT_TREAD_TWO_FWD, LEFT_TREAD_TWO_BACK)
# rightTreadOne = Motor(RIGHT_TREAD_ONE_FWD, RIGHT_TREAD_ONE_BACK)
# rightTreadTwo = Motor(RIGHT_TREAD_TWO_FWD, RIGHT_TREAD_TWO_BACK)

# # Wheg motors
# rightWheg = Motor(RIGHT_WHEG_FWD, RIGHT_WHEG_BACK)
# leftWheg = Motor(LEFT_WHEG_FWD, LEFT_WHEG_BACK)

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

"""
State interface used to determine and switch control state (from direct to drone)
0 --> direct
1 --> drone
"""
class ControlState:
    def __init__(self):
        self._state = 0

    """
    Switches control state from direct to drone (and vice versa)
    @param `control` : the current control state
    """
    def switch(self, control):
        if control == 0:
            self._state = 1
            time.sleep(2)
            s.connect((DRONE_IP, port))
            print("Switching to drone")
        elif control == 1:
            self._state = 0
            time.sleep(2)
            s.connect((CENTRAL_IP, port))
            print("Switching to central")
        else:
            pass # incorrect input
    
    """
    Returns the current state
    """
    def getState(self):
        return self._state

"""
State interface used to determine and switch camera state (from regular to IR)
"""
class CameraTypeState:
    _state = 'REG'

    """
    Switches state from reg to IR (and vice versa)
    @param `camera` : the current camera
    """
    def switch(self, camera):
        # TODO: add code to switch on microcontroller
        if camera == 'REG':
            self._state = 'IR'
        elif camera == 'IR':
            self._state = 'REG'
        else:
            pass # incorrect input
    
    """
    Returns the current state
    """
    def getState(self):
        return self._state

"""
State interface used to determine what position the camera is in 
"""
class CameraTelescopeState:
    def __init__(self):
        self._state = 'UP'

    """
    Switches state from up to down (and vice versa)
    @param `pos` : the current position of the camera
    """
    def switch(self, pos):
        if pos == 'UP':
            self._state = 'DOWN'
            # cameraY.backward()
        elif pos == 'DOWN':
            self._state = 'UP'
            # cameraY.forward()
        else:
            pass # incorrect input

    """
    Returns the current state
    """
    def getState(self):
        return self._state

"""
Class that defines a rover and its functionality
"""
class Rover:
    """
    Initializes an instance of Rover 
    """
    def __init__(self):
        self.loopCount = 0
        self.cameraTypeState = CameraTypeState()
        self.cameraTelescopeState = CameraTelescopeState()
        self.controlState = ControlState()
        self.on = True # Rover running
        s.connect((CENTRAL_IP, port))

    """
    Starts the rover and runs the drive loop
    @param `maxLoopCount` : how many loops to wait through in the event of an extended period of no controls transmitted
    """
    def start(self, maxLoopCount=None):
        print("Starting rover...")

        while self.on:
            self.drive()
            # If no commands are sent for an extended period of time
            if(self.loopCount > maxLoopCount):
                self.on = False

    """
    Main drive loop
    Will receive controller input from central and use them to control electronics
    """
    def drive(self):
        while True:
            # if [no controls]:
            #   self.loop_count += 1
            serializedControls = s.recv(1024)
            controls = pickle.loads(serializedControls)

            # print(controls.values())

            # These will probably have to be converted from input to output values
            rightSpeed = controls["rightJoy"]
            leftSpeed = controls["leftJoy"]

            # Whegs controls
            if(controls["rightTrigger"] > 0):
                # rightWheg.forward()
                # leftWheg.forward()
                print("Right whegs fwd")
            elif(controls["rightBumper"] > 0):
                # rightWheg.forward()
                # leftWheg.forward()
                print("Right whegs back")

            if(controls["leftTrigger"] > 0):
                # rightWheg.backward()
                # leftWheg.backward()
                print("Left whegs fwd")
            elif(controls["leftBumper"] > 0):
                # rightWheg.forward()
                # leftWheg.forward()
                print("Left whegs back")

            if(controls["controlToggle"] > 0):
                ctrl = self.controlState.getState()
                self.controlState.switch(ctrl)
                print("Control toggle")

            # Camera controls
            if(controls["cameraToggle"] > 0):
                camera = self.cameraTypeState.getState()
                self.cameraTypeState.switch(camera)
                print("Camera toggle")

            if(controls["cameraSwivelLeft"] > 0):
                # cameraX.value(0.5)
                print("Camera swivel left")
                
            if(controls["cameraSwivelRight"] > 0):
                # cameraX.value(-1)
                print("Camera swivel right")
            
            if(controls["cameraTelescope"] > 0):
                # if encoder steps < max steps
                pos = self.cameraTelescopeState.getState()
                self.cameraTelescopeState.switch(pos)
                print("Camera telescope switch")

            # Tread controls
            if(rightSpeed > 0):
                # rightTreadOne.forward(rightSpeed)
                # rightTreadTwo.forward(rightSpeed)
                print("Right treads")

            if(leftSpeed > 0):
                # leftTreadOne.forward(leftSpeed)
                # leftTreadTwo.forward(leftSpeed)
                print("Left treads")

            if(rightSpeed < 0):
                # rightTreadOne.backward(rightSpeed)
                # rightTreadTwo.backward(rightSpeed)
                print("Right treads")

            if(leftSpeed < 0):
                # leftTreadOne.backward(leftSpeed)
                # leftTreadTwo.backward(leftSpeed)
                print("Left treads")

rover = Rover()
rover.start()