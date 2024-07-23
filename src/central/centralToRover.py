"""
Transmits rover controls from central pi to controls pi

@author [Zoe Rizzo] [@zizz-0]

Date last modified: 07/23/2024
"""
 
import socket
import pygame
import pickle

IP = '172.168.10.136' # change to controls pi IP
PORT = 55555

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
print(joystick.get_name())
joystick.init()

# Controls:
#
# LJOY [Left joystick]          => left treads
# RJOY [Right joystick]         => right treads
# SE [Top left 3-way switch]    => pivoting treads
# SB [Left 3-way switch]        => camera tilt
# SC [Right 3-way switch]       => camera telescope
# SA [Left button]              => camera swivel left
# SD [Right button]             => camera swivel right
# S1 [Left slider]              => camera focus
# S2 [Right slider]             => camera zoom

# Controller inputs to transmit
buttonInputs = {
    "SA" : 0,
    "SD" : 1
}

# 0 => LJOY, 1 => RJOY
# 2 => SE, 3 => SB
# 4 => SC, 5 => S1
# 6 => S1, 7 => S2
axisInputs = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 7:0}

controls = {
    "leftTread" : 0,
    "rightTread" : 0,
    "wheg" : 0,
    "cameraTelescope" : 0,
    "cameraTilt" : 0,
    "cameraLeft" : 0,
    "cameraRight" : 0,
    "cameraZoom" : 0,
    "cameraFocus" : 0
}

"""
Class that defines a transmitter and its functionality in transmitting controls
"""
class Transmitter:
    """
    Initializes an instance of Transmitter 
    """
    def __init__(self):
        self.on = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

            if event.type == pygame.JOYBUTTONUP:
                if event.button == buttonInputs["SA"]:
                    controls["cameraLeft"] = 0
                    # print("SA UP")
                if event.button == buttonInputs["SD"]:
                    controls["cameraRight"] = 0
                    # print("SD UP")

            if event.type == pygame.JOYAXISMOTION:
                axisInputs[event.axis] = event.value

                if abs(axisInputs[0]) > 0.3:
                    controls["leftTread"] = axisInputs[0]
                    # print("LJOY: ", axisInputs[0])
                else:
                    controls["leftTread"] = 0

                if abs(axisInputs[1]) > 0.3:
                    controls["rightTread"] = axisInputs[1]
                    # print("RJOY: ", axisInputs[1])
                else:
                    controls["rightTread"] = 0

                if abs(axisInputs[2]) > 0.5:
                    controls["wheg"] = axisInputs[2]
                    # print("SE: ", axisInputs[2])
                else:
                    controls["wheg"] = 0

                if abs(axisInputs[3]) > 0.5:
                    controls["cameraTilt"] = axisInputs[3]
                    # print("SB: ", axisInputs[3])
                else:
                    controls["cameraTilt"] = 0

                if abs(axisInputs[4]) > 0.5:
                    controls["cameraTelescope"] = axisInputs[4]
                    # print("SC: ", axisInputs[4])
                else:
                    controls["cameraTelescope"] = 0
                
                if abs(axisInputs[5]) > 0.5:
                    controls["cameraFocus"] = axisInputs[5]
                    # print("S1: ", axisInputs[5])
                else:
                    controls["cameraZoom"] = 0

                if abs(axisInputs[7]) > 0.5:
                    controls["cameraZoom"] = axisInputs[7]
                    # print("S2: ", axisInputs[7])
                else:
                    controls["cameraZoom"] = 0
            
        # if(self.on):
        #     self.sendContinuous()

    def sendContinuous(self):
        serializedControls = pickle.dumps(controls)
        self.sock.sendto(serializedControls, (IP, PORT))

        val = False
        for x in controls.values():
            if x != 0:
                val = True
        
        if(val):
            print(controls.values())


transmit = Transmitter()
transmit.start()