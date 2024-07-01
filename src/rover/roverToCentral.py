"""
Transmits rover video to central either directly or through drone
Receives control code from central or drone and runs on rover

@author Zoe [@zizz-0]

Date last modified: 07/01/2024
"""

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

# Controller inputs to receive from central
controls = {
    "rightJoy": 0,
    "leftJoy": 0,
    "rightTrigger": 0,
    "leftTrigger": 0,
    "rightBumper": 0,
    "leftBumper": 0,
    "cameraToggle": 0,
    "controlToggle": 0,
    "cameraTelescopeUp": 0,
    "cameraTelescopeDown": 0,
    "cameraSwivelLeft": 0,
    "cameraSwivelRight": 0
}

# 0, 1, or -1
# 0 --> off
# 1 --> fwd
# -1 --> back
rightWheg = 0
leftWheg = 0

rightSpeed = 0
leftSpeed = 0


# Electronics declarations
cameraX = Servo(CAMERA_X) # Camera swivel
cameraEncoder = RotaryEncoder(CAMERA_ENCODER_ONE, CAMERA_ENCODER_TWO, max_steps=10)
cameraY = Motor(CAMERA_Y_FWD, CAMERA_Y_BACK) # Camera telecoping

# Tread drive motors
leftTreadOne = Motor(LEFT_TREAD_ONE_FWD, LEFT_TREAD_ONE_BACK)
leftTreadTwo = Motor(LEFT_TREAD_TWO_FWD, LEFT_TREAD_TWO_BACK)
rightTreadOne = Motor(RIGHT_TREAD_ONE_FWD, RIGHT_TREAD_ONE_BACK)
rightTreadTwo = Motor(RIGHT_TREAD_TWO_FWD, RIGHT_TREAD_TWO_BACK)

# Wheg motors
rightWheg = Motor(RIGHT_WHEG_FWD, RIGHT_WHEG_BACK)
leftWheg = Motor(LEFT_WHEG_FWD, LEFT_WHEG_BACK)

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

class Rover:
    loopCount = 0
    cameraType = CameraTypeState

    """
    Starts the rover and runs the drive loop
    @param `max_loop_count` : how many loops to wait through in the event of an extended period of no controls transmitted
    """
    def start(self, max_loop_count=None):
        print("Starting rover...")

        self.on = True # Rover running

        while self.on:
            self.drive()
            # If no commands are sent for an extended period of time
            if(self.loop_count > max_loop_count):
                self.on = False

    """
    Main drive loop
    Will receive controller input from central and use them to control electronics
    """
    def drive(self):
        while True:
            # TODO: get controls from central
            # if [no controls]:
            #   self.loop_count += 1
            rightSpeed = controls["rightJoy"]
            leftSpeed = controls["leftJoy"]

            if(controls["rightTrigger"] > 0):
                rightWheg = 1
                print("Right trigger")
            elif(controls["rightBumper"] > 0):
                rightWheg = -1
                print("Right bumper")
            else:
                rightWheg = 0
            
            if(controls["leftTrigger"] > 0):
                leftWheg = 1
                print("Left trigger")
            elif(controls["leftBumper"] > 0):
                leftWheg = -1
                print("Left bumper")
            else:
                leftWheg = 0

            if(controls["cameraToggle"] > 0):
                self.cameraType.switch()
                print("Camera toggle")

            if(controls["cameraSwivelLeft"] > 0):
                cameraX.value(0.5)
                print("Camera swivel left")
                
            if(controls["cameraSwivelRight"] > 0):
                cameraX.value(-1)
                print("Camera swivel right")
            
            if(controls["cameraTelescopeDown"] > 0):
                # if encoder steps < max steps
                cameraY.backward()
                print("Camera telescope down")
                
            if(controls["cameraTelescopeUp"] > 0):
                # if encoder steps < max steps
                cameraY.forward()
                print("Camera telescope up")