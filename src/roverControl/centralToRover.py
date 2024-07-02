"""
Transmits rover controls either directly or through drone

@author Zoe Rizzo [@zizz-0]

Date last modified: 07/01/2024
"""

# import hid
import socket
import pygame
import json, os

hostIp = '127.0.0.1' # change later
port = 9999

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
print(joystick.get_name())
joystick.init()

with open(os.path.join("ps4Controls.json"), 'r+') as file:
    buttonKeys = json.load(file)

# 0: Left analog horizonal, 1: Left Analog Vertical, 2: Right Analog Horizontal
# 3: Right Analog Vertical 4: Left Trigger, 5: Right Trigger
analogKeys = {0:0, 1:0, 2:0, 3:0, 4:-1, 5: -1}

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

# Controller inputs to transmit
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
            # disconnect from old IP
            connect(hostIp)
        elif control == 1:
            self._state = 0
            hostIp = '127.0.0.1' # change later
            # disconnect from old IP
            connect(hostIp)
        else:
            pass # incorrect input
    
    """
    Returns the current state
    """
    def getState(self):
        return self._state

"""
Class that defines a transmitter and its functionality in transmitting controls
"""
class Transmitter:
    """
    Initializes an instance of Transmitter 
    """
    def __init__(self):
        self.controlState = ControlState()
        self.on = True

    """
    Starts the transmitter and runs the transmission loop
    """
    def start(self):
        while self.on:
            self.sendControls()

    """
    Main loop to transmit controller input
    """
    def sendControls(self):
        for event in pygame.event.get(): # get the events (update the joystick)
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == buttonKeys['circle']:
                    controls["cameraToggle"] = 1
                if event.button == buttonKeys['square']:
                    controls["controlToggle"] = 1
                if event.button == buttonKeys['triangle']:
                    controls["cameraTelescope"] = 1
                if event.button == buttonKeys['L1']:
                    controls["cameraSwivelLeft"] = 1
                if event.button == buttonKeys['R1']:
                    controls["cameraSwivelRight"] = 1
                if event.button == buttonKeys['touchpad']:
                    self.on = False

            if event.type == pygame.JOYBUTTONUP:
                if event.button == buttonKeys['circle']:
                    controls["cameraToggle"] = 0
                if event.button == buttonKeys['square']:
                    controls["controlToggle"] = 0
                if event.button == buttonKeys['triangle']:
                    controls["cameraTelescope"] = 0
                if event.button == buttonKeys['L1']:
                    controls["cameraSwivelLeft"] = 0
                if event.button == buttonKeys['R1']:
                    controls["cameraSwivelRight"] = 0

            if event.type == pygame.JOYAXISMOTION:
                analogKeys[event.axis] = event.value

                if abs(analogKeys[1]) > .4:
                    if (analogKeys[1] < -.7) or (analogKeys[1] > .7):
                        controls["leftJoy"] = analogKeys[1]
                else:
                    controls["leftJoy"] = 0

                if abs(analogKeys[3]) > .4:
                    if (analogKeys[3] < -.7) or (analogKeys[3] > .7):
                        controls["rightJoy"] = analogKeys[3]
                else:
                    controls["rightJoy"] = 0

                # Triggers
                if analogKeys[4] > 0.05:  # Left trigger
                    controls["leftTrigger"] = analogKeys[4]
                else:
                    controls["leftTrigger"] = 0
                if analogKeys[5] > 0.05:  # Right Trigger
                    controls["rightTrigger"] = analogKeys[5]
                else:
                    controls["rightTrigger"] = 0

            print(controls.values())

trans = Transmitter()
trans.start()