import serial
import time
import pygame
import pickle
 
# Adjust the port as needed
# ser = serial.Serial('/dev/ttyUSB0', 9600)

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
print(joystick.get_name())
joystick.init()

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

analogKeys = {0:0, 1:0, 2:0, 3:0, 4:-1, 5:-1}

# inputControls[11]
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

arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Allow some time for the Arduino to reset

def getCtrls():
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

    return controls

while True:
    ctrls = getCtrls()
    inputCtrls = ",".join(f"{key}:{value}" for key, value in ctrls.items())
    arduino.write(inputCtrls.encode())
    print("Sent to Arduino: ", inputCtrls)

    # RESETTING TOGGLES -- otherwise they are continuous
    controls["cameraTypeToggle"] = 0
    controls["cameraControlToggle"] = 0
    
    # time.sleep(0.1)

# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.JOYBUTTONDOWN:
#             print(event)
#         if event.type == pygame.JOYBUTTONUP:
#             print(event)
#         if event.type == pygame.JOYAXISMOTION:
#             print(event)
            
                
        
    # ser.write(inputControls) # Sending controls as a integer array
