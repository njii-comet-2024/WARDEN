"""
Transmits rover controls either directly or through drone

@author Zoe Rizzo [@zizz-0]

Date last modified: 07/01/2024
"""

import hid
import socket
import sys

# Use to find controller vendor id and product id
for device in hid.enumerate():
    print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")

gamepad = hid.device()
gamepad.open(0x045e, 0x02ff) # Controller vendor id, product id
gamepad.set_nonblocking(True)

hostIp = '127.0.0.1' # change later
port = 9999

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
State interface used to determine and switch control state (from direct to drone)
0 --> direct
1 --> drone
"""
class ControlState:
    _state = 0

    """
    Switches state from reg to IR (and vice versa)
    @param `control` : the current control
    """
    def switch(self, control):
        if control == 0:
            self._state = 1
            hostIp = '127.0.0.1' # change later
        elif control == 1:
            self._state = 0
            hostIp = '127.0.0.1' # change later
        else:
            pass # incorrect input
    
    """
    Returns the current state
    """
    def getState(self):
        return self._state

class Drone:
    loopCount = 0

    def start(self, maxLoopCount=None):
        self.on = True
        while self.on:
            self.sendControls()
            if(self.loopCount > maxLoopCount):
                    self.on = False

    def sendControls():
        controlState = ControlState()
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
                ctrl = controlState.getState()
                controlState.switch(ctrl)
            
            # TODO: add code to connect to IP address and transmit to rover or drone