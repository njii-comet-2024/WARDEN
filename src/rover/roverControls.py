"""
Receives control code from central and runs on rover

@author [Zoe Rizzo] [@zizz-0]
        [Christopher Prol] [@prolvalone]
        [vito tribuzio] [@Snoopy-0]
        [Soumya Khera] [@soumya-khera]

Date last modified: 07/17/2024
"""
# Libraries
import pickle
import socket
from gpiozero import Motor
from gpiozero import Servo
import RPi.GPIO as GPIO

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
STEP_OPTO = 0
STEP_DIR = 0
STEP_ENA = 0

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

GPIO.setup(STEP_OPTO, GPIO.OUT)
GPIO.setup(STEP_DIR, GPIO.OUT)
GPIO.setup(STEP_ENA, GPIO.OUT)

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

        leftSpeed = abs(controls["leftTread"])
        rightSpeed = abs(controls["rightTread"])
        zoomPos = controls["cameraZoom"]

        if(controls["leftTread"] > 0):
            leftMainTread.forward(leftSpeed)
            leftWhegTread.forward(leftSpeed)
            ctrls.append("Left fwd")

        if(controls["leftTread"] < 0):
            leftMainTread.backward(leftSpeed)
            leftWhegTread.backward(leftSpeed)
            ctrls.append("Left back")

        if(controls["rightTread"] > 0):
            rightMainTread.forward(rightSpeed)
            rightWhegTread.forward(rightSpeed)
            ctrls.append("Right fwd")

        if(controls["rightTread"] < 0):
            rightMainTread.backward(rightSpeed)
            rightWhegTread.backward(rightSpeed)
            ctrls.append("Right back")

        # not fully sure about OPTO pins or ENA pins (some online code says LOW to enable but some says HIGH)
        if(controls["leftWheg"] < 0):
            GPIO.output(STEP_ENA, GPIO.LOW)
            GPIO.output(STEP_DIR, GPIO.HIGH)

            GPIO.output(STEP_OPTO, GPIO.HIGH)
            GPIO.output(STEP_OPTO, GPIO.LOW)
            ctrls.append("Whegs up")

        if(controls["leftWheg"] > 0):
            GPIO.output(STEP_ENA, GPIO.LOW)
            GPIO.output(STEP_DIR, GPIO.LOW)

            GPIO.output(STEP_OPTO, GPIO.HIGH)
            GPIO.output(STEP_OPTO, GPIO.LOW)
            ctrls.append("Whegs down")
        
        if(controls["rightWheg"] < 0):
            GPIO.output(STEP_ENA, GPIO.LOW)
            GPIO.output(STEP_DIR, GPIO.HIGH)

            GPIO.output(STEP_OPTO, GPIO.HIGH)
            GPIO.output(STEP_OPTO, GPIO.LOW)
            ctrls.append("Whegs up")

        if(controls["rightWheg"] > 0):
            GPIO.output(STEP_ENA, GPIO.LOW)
            GPIO.output(STEP_DIR, GPIO.LOW)

            GPIO.output(STEP_OPTO, GPIO.HIGH)
            GPIO.output(STEP_OPTO, GPIO.LOW)
            ctrls.append("Whegs down")

        if(controls["cameraTelescope"] < 0):
            # find max
            # if telePos < max
            telescope.forward()
            telePos += 0.01
            ctrls.append("Telescope up")
        
        if(controls["cameraTelescope"] > 0):
            if(telePos > 0):
                telescope.backward()
                telePos -= 0.01
                ctrls.append("Telescope down")
                ctrls.append(telePos)
            # else:
            #     ctrls.append("TELE END")

        if(controls["cameraTilt"] < 0):
            if(tiltPos < 1):
                tiltPos += 0.01
                tilt.value = tiltPos
                ctrls.append("Tilt up")
                ctrls.append(tiltPos)
            # else:
            #     ctrls.append("TILT END")
        
        if(controls["cameraTilt"] > 0):
            if(tiltPos > -1):
                tiltPos -= 0.01
                tilt.value = tiltPos
                ctrls.append("Tilt down")
                ctrls.append(tiltPos)
            # else:
            #     ctrls.append("TILT END")

        if(controls["cameraLeft"] < 0):
            if(swivelPos > -1):
                swivelPos -= 0.01
                swivel.value = swivelPos
                ctrls.append("Swivel left")
                ctrls.append(swivelPos)
            # else:
            #     ctrls.append("SWIVEL END")
        
        if(controls["cameraRight"] > 0):
            if(swivelPos < 1):
                swivelPos += 0.01
                swivel.value = swivelPos
                ctrls.append("Swivel right")
                ctrls.append(swivelPos)
            # else:
            #     ctrls.append("SWIVEL END")
        
        if(controls["cameraZoom"] != 0):
            zoom.value = zoomPos
            ctrls.append("Zoom in")

            if(controls["cameraZoom"] < 0):
                ctrls.append("Zoom in")
            else:
                ctrls.append("Zoom out")
        
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
    """
    def numToRange(num, inMin, inMax, outMin, outMax):
        return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax
                        - outMin))

rover = Rover()
rover.start()