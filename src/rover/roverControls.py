"""
Receives control code from central and runs on rover

@author [Zoe Rizzo] [@zizz-0]
        [Christopher Prol] [@prolvalone]
        [vito tribuzio] [@Snoopy-0]
        [Soumya Khera] [@soumya-khera]

Date last modified: 07/23/2024
"""
# Libraries
import pickle
import socket
import RPi.GPIO as GPIO
from gpiozero import Motor
from gpiozero import Servo
from roboclaw_3 import Roboclaw
import cv2 #sudo apt-get install python-opencv
import sys
import time
from RpiCamera import Camera
from Focuser import Focuser
import curses
from datetime import datetime

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

# Motors 5 & 6 -- Articulating treads (DM456AI)
STEPPER_AIN = 22
STEPPER_ENA = 27
STEPPER_ENA_RELAY = 23
STEPPER_DIR = 17
STEPPER_DIR_RELAY = 4

# Motor 7 -- Camera Telescope Linear Actuator
M7_IN1 = 0
M7_IN2 = 0

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

# Wheg stepper motors
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(STEPPER_DIR, GPIO.OUT)
GPIO.setup(STEPPER_ENA, GPIO.OUT)
GPIO.setup(STEPPER_ENA_RELAY, GPIO.OUT)
GPIO.setup(STEPPER_DIR, GPIO.OUT)
GPIO.setup(STEPPER_DIR_RELAY, GPIO.OUT)

# Global variables
IP = '172.168.10.136'  # change to controls pi IP
CAMERA_IP = '172.168.10.136'  # change to camera pi IP
RECV_PORT = 55555
SEND_PORT = 1111

cameraType = 0

rightSpeed = 0
leftSpeed = 0

# Servo range => (-1, 1)
tiltPos = 0
swivelPos = 0
zoomPos = 0
telePos = 0 # change to middle position

# SPEED => (0, 128)
address = 0x80
# port: ls -l /dev/serial/by-id/
rcOne = Roboclaw("/dev/ttyACM0", 38400)
rcOne.Open()

rcTwo = Roboclaw("/dev/ttyACM0", 38400)
rcTwo.Open()

auto_focus_map = []
auto_focus_idx = 0

"""
Class that defines a rover and its functionality
"""
class Rover:
    """
    Initializes an instance of Rover 
    """
    def __init__(self):
        self.loopCount = 0
        self.on = True  # Rover running

        # Socket to receive controls from central pi
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvSocket.bind((IP, RECV_PORT))
        
        # Socket to send camera pos to camera pi
        # self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    """
    Starts the rover and runs the drive loop
    @param `maxLoopCount` : how many loops to wait through in the event of an extended period of no controls transmitted
    """
    def start(self, maxLoopCount=1):
        print("Starting rover...")

        while self.on:
            self.drive()
            # self.sendToCameraPi()
            # If no commands are sent for an extended period of time
            if self.loopCount > maxLoopCount:
                self.on = False

    """
    Main drive loop
    Will receive controller input from central and run controls on rover
    """
    def drive(self):
        global zoomPos, tiltPos, swivelPos, telePos
        ctrls = []
        
        serializedControls, addr = self.recvSocket.recvfrom(1024)
        controls = pickle.loads(serializedControls)  # deserializes controls

        zoomPos = controls["cameraZoom"]

        rightSpeed = int(controls["rightTread"] * 127)
        leftSpeed = int(controls["leftTread"] * 127)

        if rightSpeed > 0:
            rcOne._write1(address, Roboclaw.Cmd.M1FORWARD, rightSpeed)
            rcOne._write1(address, Roboclaw.Cmd.M2FORWARD, leftSpeed)
            ctrls.append("Right fwd")
        else:
            rcOne._write1(address, Roboclaw.Cmd.M1BACKWARD, abs(rightSpeed))
            rcOne._write1(address, Roboclaw.Cmd.M2BACKWARD, abs(leftSpeed))
            ctrls.append("Right back")
        
        if leftSpeed > 0:
            rcTwo._write1(address, Roboclaw.Cmd.M2FORWARD, leftSpeed)
            ctrls.append("Left fwd")
        else:
            rcTwo._write1(address, Roboclaw.Cmd.M2BACKWARD, abs(leftSpeed))
            ctrls.append("Left back")

       #STEPPER CODE

        if(controls["wheg"] < 0): 
            GPIO.output(STEPPER_ENA, GPIO.HIGH)
            GPIO.output(STEPPER_ENA_RELAY, GPIO.HIGH)
            GPIO.output(STEPPER_DIR, GPIO.HIGH)
            GPIO.output(STEPPER_DIR_RELAY, GPIO.HIGH)
            ctrls.append("Whegs up")

        if(controls["wheg"] > 0):
            GPIO.output(STEPPER_ENA, GPIO.HIGH)
            GPIO.output(STEPPER_ENA_RELAY, GPIO.HIGH)
            GPIO.output(STEPPER_DIR, GPIO.LOW)
            GPIO.output(STEPPER_DIR_RELAY, GPIO.LOW)

            ctrls.append("Whegs down")

        if(controls["wheg"] > 0):                   #WHEGS OFF
            GPIO.output(STEPPER_ENA, GPIO.LOW)
            GPIO.output(STEPPER_ENA_RELAY, GPIO.LOW)
        
        #Acutator Code
        if(controls["cameraTelescope"] < 0):
            telescope.backward()
            ctrls.append("Telescope up")
        
        if(controls["cameraTelescope"] > 0):
            telescope.backward()
            ctrls.append("Telescope down")
        #Servo Code
        if(controls["cameraTilt"] < 0):
            tilt.value = -1
            ctrls.append("Tilt up")
        
        if(controls["cameraTilt"] > 0):
            tilt.value = 1
            ctrls.append("Tilt down")

        if(controls["cameraLeft"] > 0):
            swivel.value = -1
            ctrls.append("Swivel left")
        elif(controls["cameraRight"] > 0):
            swivel.value = 1
            ctrls.append("Swivel right")
        
        if(controls["cameraZoom"] != 0):
            zoom.value = zoomPos
            if(controls["cameraZoom"] < 0):
                ctrls.append("Zoom out")
            else:
                ctrls.append("Zoom in")

        if(controls["cameraFocus"] != 0):
            focus = self.numToRange(controls["cameraFocus"], -1, 1, 0, 2100)
        
        if(ctrls):
            print(ctrls)
    
    def sendToCameraPi(self):
        # re-maps camera values and converts to bytearray
        newTilt = self.numToRange(tiltPos, -1, 1, 0, 180)
        newSwivel = self.numToRange(swivelPos, -1, 1, 0, 205)
        newTele = self.numToRange(telePos, 0, 1, 0, 180) # figure out actual max
        newZoom = self.numToRange(zoomPos, -1, 1, 0, 10)
        cameraPos = [newTilt, newSwivel, newTele, newZoom]
        cameraPosByte = bytearray(cameraPos)

        self.sendSocket.sendto(cameraPosByte, (CAMERA_IP, SEND_PORT))

    """
    Maps a number from one range to another

    @param `num` : number to re-map
    @param `inMin` : original range min
    @param `inMax` : original range max
    @param `outMin` : target range min
    @param `outMax` : target range max

    @return (int) number mapped to new range
    """
    def numToRange(self, num, inMin, inMax, outMin, outMax):
        flSpeed = outMin + (float(num - inMin) / float(inMax - inMin) * (outMax
                        - outMin))
        return int(flSpeed)

rover = Rover()
rover.start()