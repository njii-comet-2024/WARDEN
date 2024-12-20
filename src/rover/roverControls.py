"""
Receives control code from central and runs on rover
Runs on Controls Pi

@author [Zoe Rizzo] [@zizz-0]
        [Christopher Prol] [@prolvalone]
        [Vito Tribuzio] [@Snoopy-0]
        [Soumya Khera] [@soumya-khera]

Date last modified: 08/05/2024
"""
# Libraries
import pickle
import socket
import RPi.GPIO as GPIO
from roboclaw_3 import Roboclaw

#These are for WARDEN and should be same for EXT since they are static IPS
#RoverCam RASPI = 192.168.110.169
#RoverCam JETSON = 192.168.110.218
#Drone =  192.168.110.228
#Rover  = 192.168.110.19
#Central = 192.168.110.5

# PINS
# IN1 => CLOCKWISE
# IN2 => COUNTER-CLOCKWISE

# Motors 5 & 6 -- Articulating treads (DM456AI)
STEPPER_AIN = 22
STEPPER_ENA = 27
STEPPER_ENA_RELAY = 23
STEPPER_DIR = 17
STEPPER_DIR_RELAY = 4

# Motor 7 -- Camera Telescope Linear Actuator
M7_IN1 = 26
M7_IN2 = 19
M7_ENA = 13

# Wheg stepper motors
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(STEPPER_DIR, GPIO.OUT)
GPIO.setup(STEPPER_ENA, GPIO.OUT)
GPIO.setup(STEPPER_ENA_RELAY, GPIO.OUT)
GPIO.setup(STEPPER_DIR_RELAY, GPIO.OUT)

#Actuator Motor
GPIO.setup(M7_IN1, GPIO.OUT)
GPIO.setup(M7_IN2, GPIO.OUT)
GPIO.setup(M7_ENA, GPIO.OUT)

# Global variables
IP = '192.168.110.19'  # Controls Pi IP
PORT = 55555

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

rcRight = Roboclaw("/dev/ttyACM0", 38400) # right treads
rcRight.Open()

rcLeft = Roboclaw("/dev/ttyACM1", 38400) # left treads
rcLeft.Open()

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
        self.recvSocket.bind((IP, PORT))
        
        self.recv = 0

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
    Will receive controller input from central and run controls on rover
    """
    def drive(self):
        global zoomPos, tiltPos, swivelPos, telePos
        ctrls = []
        
        try: 
            serializedControls, addr = self.recvSocket.recvfrom(1024)
            controls = pickle.loads(serializedControls)  # deserializes controls
        except socket.error: 
            controls = {
                "leftTread" : 0,
                "rightTread" : 0,
                "wheg" : 0,
                "cameraTelescope" : 0,
                "end" : 0
            }
            

        if(addr):
            self.recv += 1

        if(self.recv == 1):
            print("Connected to ", addr)

        if(controls["end"] > 0):
            print("END")
            self.on = False
            # return
        
        # max speed capped at 60/128 -- can be changed depending on use case
        rightSpeed = int(controls["rightTread"] * 30)
        leftSpeed = int(controls["leftTread"] * 30)

        if rightSpeed > 0:
            rcRight._write1(address, Roboclaw.Cmd.M1FORWARD, rightSpeed)
            rcRight._write1(address, Roboclaw.Cmd.M2FORWARD, rightSpeed)
            ctrls.append("Right fwd")
        else:
            rcRight._write1(address, Roboclaw.Cmd.M1BACKWARD, abs(rightSpeed))
            rcRight._write1(address, Roboclaw.Cmd.M2BACKWARD, abs(rightSpeed))
            if(rightSpeed != 0):
                ctrls.append("Right back")
        
        if leftSpeed > 0:
            rcLeft._write1(address, Roboclaw.Cmd.M1BACKWARD, leftSpeed)
            rcLeft._write1(address, Roboclaw.Cmd.M2BACKWARD, leftSpeed)
            ctrls.append("Left fwd")
        else:
            rcLeft._write1(address, Roboclaw.Cmd.M1FORWARD, abs(leftSpeed))
            rcLeft._write1(address, Roboclaw.Cmd.M2FORWARD, abs(leftSpeed))
            if(leftSpeed != 0):
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

        if(controls["wheg"] == 0): # WHEGS OFF
            GPIO.output(STEPPER_ENA, GPIO.LOW)
            GPIO.output(STEPPER_ENA_RELAY, GPIO.LOW)
        
        #LINEAR ACTUATOR CODE
        if(controls["cameraTelescope"] < 0): # UP
            GPIO.output(M7_IN1, GPIO.LOW)
            GPIO.output(M7_IN2, GPIO.HIGH)
            GPIO.output(M7_ENA, GPIO.HIGH)
            ctrls.append("Telescope up")
        
        if(controls["cameraTelescope"] > 0): # DOWN
            GPIO.output(M7_IN1, GPIO.HIGH)
            GPIO.output(M7_IN2, GPIO.LOW)
            GPIO.output(M7_ENA, GPIO.HIGH)
            ctrls.append("Telescope down")
        
        if(controls["cameraTelescope"] == 0): # OFF
            GPIO.output(M7_ENA, GPIO.LOW)
            GPIO.output(M7_IN1, GPIO.LOW)
            GPIO.output(M7_IN2, GPIO.LOW)
       
        if(ctrls):
            print(ctrls)

rover = Rover()
rover.start()