"""
Transmits rover controls either directly or through drone

@author Zoe Rizzo [@zizz-0]

Date last modified: 07/01/2024
"""

import hid
import socket
import sys
import time
from inputs import devices
import pygame
import json, os

# Use to find controller vendor id and product id
# for device in hid.enumerate():
#     print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")

# gamepad = hid.device()
# gamepad.open(0x054c, 0x09cc) # Controller vendor id, product id
# gamepad.set_nonblocking(True)

hostIp = '127.0.0.1' # change later
port = 9999

# while True:
#     report = gamepad.read(64)
#     if report:
#         print(report)
#         time.sleep(1)

# for device in devices:
#     print(device)

# print(devices.gamepads)
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

while True:
    for event in pygame.event.get(): # get the events (update the joystick)
        if event.type == pygame.QUIT:
            break
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == buttonKeys['leftArrow']:
                print("left arrow")
            if event.button == buttonKeys['rightArrow']:
                print("right arrow")
            if event.button == buttonKeys['upArrow']:
                print("up arrow")
            if event.button == buttonKeys['downArrow']:
                print("down arrow")
            if event.button == buttonKeys['x']:
                print("x")
            if event.button == buttonKeys['circle']:
                print("circle")
            if event.button == buttonKeys['square']:
                print("square")
            if event.button == buttonKeys['triangle']:
                print("triangle")
            if event.button == buttonKeys['L1']:
                print("L1")
            if event.button == buttonKeys['R1']:
                print("R1")
        if event.type == pygame.JOYAXISMOTION:
            analogKeys[event.axis] = event.value

            # Horizontal analog LEFT JOY
            if abs(analogKeys[0]) > .4:
                if analogKeys[0] < -.7:
                    print("LEFT JOY left")
                if analogKeys[0] > .7:
                    print("LEFT JOY right")
            # Vertical analog LEFT JOY
            if abs(analogKeys[1]) > .4:
                if analogKeys[1] < -.7:
                    print("LEFT JOY up")
                if analogKeys[1] > .7:
                    print("LEFT JOY down")
  
            # Horizontal analog RIGHT JOY
            if abs(analogKeys[2]) > .4:
                if analogKeys[2] < -.7:
                    print("RIGHT JOY left")
                if analogKeys[2] > .7:
                    print("RIGHT JOY right")
            # Vertical analog RIGHT JOY
            if abs(analogKeys[3]) > .4:
                if analogKeys[3] < -.7:
                    print("RIGHT JOY up")
                if analogKeys[3] > .7:
                    print("RIGHT JOY down")

            # Triggers
            if analogKeys[4] > 0:  # Left trigger
                print("left trigger")
            if analogKeys[5] > 0:  # Right Trigger
                print("right trigger")

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
Class that defines a drone and its functionality in transmitting controls
"""
class Drone:
    """
    Initializes an instance of Drone 
    """
    def __init__(self):
        self.controlState = ControlState()
        self.on = True

    """
    Starts the drone transmitter and runs the transmission loop
    """
    def start(self):
        while self.on:
            self.sendControls()

    """
    Main loop to transmit controller input
    """
    def sendControls(self):
        controlInput = gamepad.read(64)
        if controlInput:
            print(controlInput)
        
            controls["leftJoy"] = controlInput[0]
            controls["rightJoy"] = controlInput[0]
            controls["rightTrigger"] = controlInput[0]
            controls["leftTrigger"] = controlInput[0]
            controls["cameraToggle"] = controlInput[0]
            controls["controlToggle"] = controlInput[0]
            controls["cameraTelescope"] = controlInput[0]
            controls["cameraSwivelLeft"] = controlInput[0]
            controls["cameraSwivelRight"] = controlInput[0]

            if(controls["controlToggle"] > 0):
                print("Control switched")
                ctrl = self.controlState.getState()
                self.controlState.switch(ctrl)
            
            # TODO: add code to connect to IP address and transmit to rover or drone