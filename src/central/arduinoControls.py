import serial
import time
import pygame
import pickle
 
# Adjust the port as needed
ser = serial.Serial('/dev/ttyUSB0', 9600)

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
print(joystick.get_name())
joystick.init()

joyControls = {
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

analogKeys = {0:0, 1:0, 2:0, 3:0, 4:-1, 5:-1}

int inputControls[11]
"""
0  => left joystick analog  => left treads
1  => right stick analog    => right treads
2  => left trigger          => left whegs fwd
3  => right trigger         => right whegs fwd
4  => left bumper           => left whegs back
5  => right bumper          => right whegs back
6  => x                     => camera tilt / telescope down
7  => circle                => camera swivel right
8  => triangle              => camera tilt / telescope up
9  => square                => camera swivel left
10 => left circle           => camera type toggle 
11 => right circle          => camera control toggle
"""

while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            print(event)
        if event.type == pygame.JOYAXISMOTION:
            print(event)
            
                
        
    # ser.write(encoded) # Sending controls as a dictionary
