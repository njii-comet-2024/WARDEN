"""
Transmits rover controls from central

@author [Zoe Rizzo] [@zizz-0]

Date last modified: 07/11/2024
"""

import socket
import pygame
import pickle

ROVER_IP = '192.168.110.228' # change to rover IP
PORT = 55555

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
print(joystick.get_name())
joystick.init()

# s = socket.socket() # TCP

# Controls:
#
# LJOY [Left joystick]          => left treads
# RJOY [Right joystick]         => right treads
# SE [Top left 3-way switch]    => left pivoting tread
# SF [Top right 3-way switch]   => right pivoting tread
# SB [Left 3-way switch]        => camera tilt
# SC [Right 3-way switch]       => camera telescope
# SA [Left button]              => camera swivel left
# SD [Right button]             => camera swivel right
# S1 [Left slider]              => camera type toggle
# S2 [Right slider]             => camera zoom

# Controller inputs to transmit
buttonInputs = {
    "SA" : 0,
    "SD" : 1,
    "S1" : 2
}

# 0 => RJOY, 1 => LJOY
# 2 => SE, 3 => SF
# 4 => SB, 5 => SC
# 7 => S2
axisInputs = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 7:0}

controls = {
    "leftTread" : 0,
    "rightTread" : 0,
    "leftWheg" : 0,
    "rightWheg" : 0,
    "cameraTypeToggle" : 0,
    "cameraTelescope" : 0,
    "cameraTilt" : 0,
    "cameraLeft" : 0,
    "cameraRight" : 0,
    "cameraZoom" : 0
}

# PS4
# 0: Left analog horizonal, 1: Left Analog Vertical, 2: Right Analog Horizontal
# 3: Right Analog Vertical 4: Left Trigger, 5: Right Trigger
# analogKeys = {0:0, 1:0, 2:0, 3:0, 4:-1, 5:-1}

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
            # print(event)
            if event.type == pygame.QUIT:
                break
            
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == buttonInputs["SA"]:
                    controls["cameraLeft"] = 1
                    # print("SA DOWN")
                if event.button == buttonInputs["SD"]:
                    controls["cameraRight"] = 1
                    # print("SD DOWN")
                if event.button == buttonInputs["S1"]:
                    controls["cameraTypeToggle"] = 1
                    # print("S1 DOWN")

            if event.type == pygame.JOYBUTTONUP:
                if event.button == buttonInputs["SA"]:
                    controls["cameraLeft"] = 0
                    # print("SA UP")
                if event.button == buttonInputs["SD"]:
                    controls["cameraRight"] = 0
                    # print("SD UP")
                if event.button == buttonInputs["S1"]:
                    controls["cameraTypeToggle"] = 1
                    # print("S1 UP")

            if event.type == pygame.JOYAXISMOTION:
                axisInputs[event.axis] = event.value

                if abs(axisInputs[0]) > 0.1:
                    controls["leftTread"] = axisInputs[0]
                    # print("LJOY: ", axisInputs[0])
                else:
                    controls["leftTread"] = 0

                if abs(axisInputs[1]) > 0.1:
                    controls["rightTread"] = axisInputs[1]
                    # print("RJOY: ", axisInputs[1])
                else:
                    controls["rightTread"] = 0

                if abs(axisInputs[2]) > 0.5:
                    controls["leftWheg"] = axisInputs[2]
                    # print("SE: ", axisInputs[2])
                else:
                    controls["leftWheg"] = 0

                if abs(axisInputs[3]) > 0.5:
                    controls["rightWheg"] = axisInputs[3]
                    # print("SF: ", axisInputs[3])
                else:
                    controls["rightWheg"] = 0

                if abs(axisInputs[4]) > 0.5:
                    controls["cameraTilt"] = axisInputs[4]
                    # print("SB: ", axisInputs[4])
                else:
                    controls["cameraTilt"] = 0

                if abs(axisInputs[5]) > 0.5:
                    controls["cameraTelescope"] = axisInputs[5]
                    # print("SD: ", axisInputs[5])
                else:
                    controls["cameraTelescope"] = 0

                if abs(axisInputs[7]) > 0.5:
                    controls["cameraZoom"] = axisInputs[7]
                    # print("SD: ", axisInputs[5])
                else:
                    controls["cameraZoom"] = 0
            
        if(self.on):
            self.sendContinuous()

        # RESETTING TOGGLES -- otherwise they are continuous
        controls["cameraTypeToggle"] = 0

    def sendContinuous(self):
        serializedControls = pickle.dumps(controls)

        # self.c.send(serializedControls) # TCP
        self.sock.sendto(serializedControls, (ROVER_IP, PORT))

        val = False
        for x in controls.values():
            if x != 0:
                val = True
        
        if(val):
            print(controls.values())
        # print("Continuous")


transmit = Transmitter()
transmit.start()