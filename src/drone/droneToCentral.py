'''
Code to send images from drone to central
from external camera mounted on the bottom

@author [Vito Tribuzio][Snoopy-0]

Date last modified: 06/16/2024
'''
import socket
import struct
import pickle
import time
import cv2
import numpy as np
from picamera2 import Picamera2

#These are for WARDEN and should be same for EXT since they are static IPS
#RoverCam = 192.168.110.169
#Drone =  192.168.110.228
#Rover  = 192.168.110.19
#Central = 192.168.110.5

# Socket parameters
serverIp = '192.168.110.5'  # Replace with receiver's IP address
serverPort = 5005

# Initialize socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverIp, serverPort))
connection = clientSocket.makefile('wb')

# Initialize Picamera2
camera = Picamera2()
cameraConfig = camera.create_still_configuration(main={"size": (1024, 600)}, lores={"size": (1024, 600)}, display="lores")
camera.configure(cameraConfig)
camera.start()

try:
    while True:
        # Capture frame
        frame = camera.capture_array("main")
        
        # Compress frame
        _, frame_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        data = pickle.dumps(frame_encoded, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Pack message length and frame data
        message = struct.pack("Q", len(data)) + data
        
        # Send message
        connection.write(message)
        connection.flush()

except KeyboardInterrupt:
    pass

finally:
    # Release resources
    connection.close()
    clientSocket.close()
    camera.stop()
