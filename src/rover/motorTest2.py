# Complete example of using the RoboClaw library

#import the relevant code from the RoboClaw library

from roboclaw_3 import Roboclaw

# address of the RoboClaw as set in Motion Studio

address = 0x80

# Creating the RoboClaw object, serial port and baudrate passed

roboclaw = Roboclaw("/dev/ttyACM0", 115200)

# Starting communication with the RoboClaw hardware

roboclaw.Open()

# Start motor 1 in the forward direction at half speed

while True:
    roboclaw.ForwardM1(address, 63)
