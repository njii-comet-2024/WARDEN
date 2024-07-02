"""
Transmits rover video to central either directly or through drone
Receives control code from central or drone and runs on rover

@author Zoe Rizzo [@zizz-0]

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

# Controls:
#
# Right joystick  --> right treads
# Left joystick   --> left treads
# Right trigger   --> whegs fwd
# Left trigger    --> whegs back
# Right bumper    --> camera swivel right
# Left bumper     --> camera swivel left
# B               --> camera type toggle
# X               --> camera telescope toggle
# Y               --> control toggle [drone vs direct]

# Controller inputs to receive from central
controls = {
    "rightJoy": 0,
    "leftJoy": 0,
    "rightTrigger": 0,
    "leftTrigger": 0,
    "cameraToggle": 0,
    "controlToggle": 0,
    "cameraTelescope": 0,
    "cameraSwivelLeft": 0,
    "cameraSwivelRight": 0
}

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
Function to connect to a certain IP address
@param `ip` : IP address of either drone or rover
"""
def connect(ip):
    print("fill out later")

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
            hostIp = '127.0.0.1' # change later
            connect(hostIp)
        elif control == 1:
            self._state = 0
            hostIp = '127.0.0.1' # change later
            connect(hostIp)
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
            cameraY.backward()
        elif pos == 'DOWN':
            self._state = 'UP'
            cameraY.forward()
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
        self.on = True # Rover running

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
            # TODO: get controls from central
            # if [no controls]:
            #   self.loop_count += 1

            # These will probably have to be converted from input to output values
            rightSpeed = controls["rightJoy"]
            leftSpeed = controls["leftJoy"]

            # Whegs controls
            if(controls["rightTrigger"] > 0):
                rightWheg.forward()
                leftWheg.forward()
                print("Whegs fwd")
            elif(controls["leftTrigger"] > 0):
                rightWheg.backward()
                leftWheg.backward()
                print("Whegs back")

            # Camera controls
            if(controls["cameraToggle"] > 0):
                camera = CameraTypeState.getState()
                self.cameraTypeState.switch(camera)
                print("Camera toggle")

            if(controls["cameraSwivelLeft"] > 0):
                cameraX.value(0.5)
                print("Camera swivel left")
                
            if(controls["cameraSwivelRight"] > 0):
                cameraX.value(-1)
                print("Camera swivel right")
            
            if(controls["cameraTelescope"] > 0):
                # if encoder steps < max steps
                pos = CameraTelescopeState.getState()
                self.cameraTelescopeState.switch(pos)
                print("Camera telescope switch")

            # Tread controls
            if(rightSpeed > 0):
                rightTreadOne.forward(rightSpeed)
                rightTreadTwo.forward(rightSpeed)
                print("Right treads")

            if(leftSpeed > 0):
                leftTreadOne.forward(leftSpeed)
                leftTreadTwo.forward(leftSpeed)
                print("Left treads")

            if(rightSpeed < 0):
                rightTreadOne.backward(rightSpeed)
                rightTreadTwo.backward(rightSpeed)
                print("Right treads")

            if(leftSpeed < 0):
                leftTreadOne.backward(leftSpeed)
                leftTreadTwo.backward(leftSpeed)
                print("Left treads")