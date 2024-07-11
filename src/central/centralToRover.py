"""
Transmits rover controls either directly or through drone

@author [Zoe Rizzo] [@zizz-0]

Date last modified: 07/09/2024
"""

# import hid
import socket
import pygame
import json, os
import pickle
import serial

DRONE_IP = '192.168.110.228' # change to drone IP
CENTRAL_IP = '192.168.110.228' # change to central IP
PORT = 55555

IP = CENTRAL_IP

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
print(joystick.get_name())
joystick.init()

# s = socket.socket() # TCP

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
inputs = {
    "x" : 0,
    "circle" : 1,
    "triangle" : 2,
    "square" : 3,
    "leftBumper" : 4,
    "rightBumper" : 5,
    "leftTrigger" : 6,
    "rightTrigger" : 7,
    "leftCircle" : 8,
    "rightCircle" : 9,
    "leftJoyClick" : 12,
    "rightJoyClick" : 13
}

controls = {
    "leftTread" : 0,
    "rightTread" : 0,
    "leftWhegFwd" : 0,
    "leftWhegBack" : 0,
    "rightWhegFwd" : 0,
    "rightWhegBack" : 0,
    "cameraTypeToggle" : 0,
    "cameraControlToggle" : 0,
    "cameraUp" : 0,
    "cameraDown" : 0,
    "cameraLeft" : 0,
    "cameraRight" : 0
}

# 0: Left analog horizonal, 1: Left Analog Vertical, 2: Right Analog Horizontal
# 3: Right Analog Vertical 4: Left Trigger, 5: Right Trigger
analogKeys = {0:0, 1:0, 2:0, 3:0, 4:-1, 5: -1}

"""
Class that defines a transmitter and its functionality in transmitting controls
"""
class Transmitter:
    """
    Initializes an instance of Transmitter 
    """
    def __init__(self):
        self.on = True
        
        # UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # TCP
        # s.bind((CENTRAL_IP, port))
        # s.listen()
        # print("Listening for connection")
        # self.c, self.addr = s.accept()
        # print("Got connection from", self.addr)

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
                # Camera controls
                if event.button == inputs['circle']: # continuously press
                    controls["cameraRight"] = 1
                if event.button == inputs['square']: # continuously press
                    controls["cameraLeft"] = 1
                if event.button == inputs['triangle']: # continuously press
                    controls["cameraUp"] = 1
                if event.button == inputs['x']: # continuously press
                    controls["cameraDown"] = 1

                # Camera toggles
                if event.button == inputs['leftCircle']: # continuously press
                    controls["leftWhegBack"] = 1
                if event.button == inputs['rightCircle']: # continuously press
                    controls["rightWhegBack"] = 1

                # Wheg controls
                if event.button == inputs['leftBumper']:
                    controls["cameraTypeToggle"] = 1
                if event.button == inputs['rightBumper']:
                    controls["cameraControlToggle"] = 1


            if event.type == pygame.JOYBUTTONUP:
                # Camera controls
                if event.button == inputs['circle']: # continuously press
                    controls["cameraRight"] = 0
                if event.button == inputs['square']: # continuously press
                    controls["cameraLeft"] = 0
                if event.button == inputs['triangle']: # continuously press
                    controls["cameraUp"] = 0
                if event.button == inputs['x']: # continuously press
                    controls["cameraDown"] = 0

                # Camera toggles
                if event.button == inputs['leftCircle']: # continuously press
                    controls["leftWhegBack"] = 0
                if event.button == inputs['rightCircle']: # continuously press
                    controls["rightWhegBack"] = 0

                # Wheg controls
                if event.button == inputs['leftBumper']:
                    controls["cameraTypeToggle"] = 0
                if event.button == inputs['rightBumper']:
                    controls["cameraControlToggle"] = 0

            if event.type == pygame.JOYAXISMOTION:
                analogKeys[event.axis] = event.value

                if abs(analogKeys[1]) > .4:
                    if (analogKeys[1] < -.7) or (analogKeys[1] > .7): # continuously pressed
                        controls["leftJoy"] = analogKeys[1]
                else:
                    controls["leftJoy"] = 0

                if abs(analogKeys[3]) > .4:
                    if (analogKeys[3] < -.7) or (analogKeys[3] > .7):
                        controls["leftTread"] = analogKeys[3]
                else:
                    controls["rightTread"] = 0

                # Triggers
                if analogKeys[4] > 0.05:  # Left trigger
                    controls["leftWhegFwd"] = analogKeys[4]
                else:
                    controls["leftWhegFwd"] = 0
                if analogKeys[5] > 0.05:  # Right Trigger
                    controls["rightWhegFwd"] = analogKeys[5]
                else:
                    controls["rightWhegFwd"] = 0
            
        if(self.on):
            self.sendContinuous()

        # RESETTING TOGGLES -- otherwise they are continuous
        controls["cameraTypeToggle"] = 0
        controls["cameraControlToggle"] = 0

    def sendContinuous(self):
        serializedControls = pickle.dumps(controls)

        # self.c.send(serializedControls) # TCP
        self.sock.sendto(serializedControls, (IP, PORT))

        val = False
        for x in controls.values():
            if x != 0:
                val = True
        
        if(val):
            print(controls.values())
        # print("Continuous")


transmit = Transmitter()
transmit.start()