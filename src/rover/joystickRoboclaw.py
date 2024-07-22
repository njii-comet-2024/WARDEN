import pygame
import time
from roboclaw import Roboclaw

# Initialize pygame for joystick control
pygame.init()
pygame.joystick.init()

# Initialize the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Initialize Roboclaw (replace 'COM3' with your actual port)
rc = Roboclaw("/dev/ttyACM0", 38400)
rc.Open()

# Roboclaw address
address = 0x80

# Function to control the motors
def control_motors():
    while True:
        # Process pygame events to update joystick state
        pygame.event.pump()
        
        # Get joystick axis
        left_axis = joystick.get_axis(1)
        right_axis = joystick.get_axis(3)

        print(joystick.get_axis(3))
        
        # Map joystick value (-1 to 1) to motor speed (0 to 127)
        speed_left = int(left_axis * 127)
        speed_right = int(right_axis * 127)

        # Forward for positive axis, backward for negative axis
        if speed_left > 0:
            rc._write1(address, Roboclaw.Cmd.M1FORWARD, speed_left)
        else:
            rc._write1(address, Roboclaw.Cmd.M1BACKWARD, abs(speed_left))

        if speed_right > 0:
            rc._write1(address, Roboclaw.Cmd.M2FORWARD, speed_right)
        else:
            rc._write1(address, Roboclaw.Cmd.M2BACKWARD, abs(speed_right))

        # Add a small delay to prevent excessive CPU usage
        time.sleep(0.1)

# Run the control function
try:
    control_motors()
except KeyboardInterrupt:
    # Stop motors on interrupt
    rc._write1(address, Roboclaw.Cmd.M1FORWARD, 0)
    rc._write1(address, Roboclaw.Cmd.M2FORWARD, 0)
    rc._port.close()
    print("Program terminated and motors stopped.")
