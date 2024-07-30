"""
Receives control code from central and runs on rover

@author [Zoe Rizzo] [@zizz-0]
        [Christopher Prol] [@prolvalone]
        [vito tribuzio] [@Snoopy-0]
        [Soumya Khera] [@soumya-khera]

Date last modified: 07/26/2024
"""
# Libraries
import pickle
import socket
import RPi.GPIO as GPIO
from roboclaw_3 import Roboclaw

# PINS
# IN1 => CLOCKWISE
# IN2 => COUNTER-CLOCKWISE

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

# Camera motor/servos
#telescope = Motor(M7_IN1, M7_IN2)

# Wheg stepper motors
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(STEPPER_DIR, GPIO.OUT)
GPIO.setup(STEPPER_ENA, GPIO.OUT)
GPIO.setup(STEPPER_ENA_RELAY, GPIO.OUT)
GPIO.setup(STEPPER_DIR, GPIO.OUT)
GPIO.setup(STEPPER_DIR_RELAY, GPIO.OUT)

# Global variables
IP = '192.168.10.148'  # change to controls pi IP
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
rcLeft = Roboclaw("/dev/ttyACM0", 38400) # left treads
rcLeft.Open()

rcRight = Roboclaw("/dev/ttyACM1", 38400) # right treads
rcRight.Open()

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
        
        self.recv = 0

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

        # if(addr):
        #     self.recv = 1

        # if(self.recv == 1):
        #     print("Connected to ", addr)

        controls = pickle.loads(serializedControls)  # deserializes controls

        zoomPos = controls["cameraZoom"]

        rightSpeed = int(controls["rightTread"] * 80)
        leftSpeed = int(controls["leftTread"] * 80)

        if rightSpeed > 0:
            rcRight._write1(address, Roboclaw.Cmd.M1BACKWARD, rightSpeed)
            rcRight._write1(address, Roboclaw.Cmd.M2BACKWARD, rightSpeed)
            ctrls.append("Right fwd")
        else:
            rcRight._write1(address, Roboclaw.Cmd.M1FORWARD, abs(rightSpeed))
            rcRight._write1(address, Roboclaw.Cmd.M2FORWARD, abs(rightSpeed))
            ctrls.append("Right back")
        
        if leftSpeed > 0:
            rcLeft._write1(address, Roboclaw.Cmd.M1FORWARD, leftSpeed)
            rcLeft._write1(address, Roboclaw.Cmd.M2FORWARD, leftSpeed)
            ctrls.append("Left fwd")
        else:
            rcLeft._write1(address, Roboclaw.Cmd.M1BACKWARD, abs(leftSpeed))
            rcLeft._write1(address, Roboclaw.Cmd.M2BACKWARD, abs(leftSpeed))
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
        # if(controls["cameraTelescope"] < 0):
        #     telescope.backward()
        #     ctrls.append("Telescope up")
        
        # if(controls["cameraTelescope"] > 0):
        #     telescope.backward()
        #     ctrls.append("Telescope down")
       
        if(ctrls):
            print(ctrls)

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