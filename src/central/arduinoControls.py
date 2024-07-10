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
    "up" : 11,
    "down" : 12
}

controls = {
    "upArrow" : 0,
    "downArrow" : 0
}
 
while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            print(event)
            if event.button == 11:
                controls["upArrow"] = 1
                print("UP")
            if event.button == 12:
                controls["downArrow"] = 1
                print("DOWN")
                
        if event.type == pygame.JOYBUTTONUP:
            print(event)
            if event.button == 11:
                controls["upArrow"] = 0
            if event.button == 12:
                controls["downArrow"] = 0
                
    # encoded = pickle.dumps(controls)
        
    # ser.write(encoded) # Sending controls as a dictionary
