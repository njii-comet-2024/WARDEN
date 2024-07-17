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
from picamera2.encoders import Quality
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# Socket parameters
server_ip = 'RECEIVER_IP_ADDRESS'  # Replace with receiver's IP address
server_port = 5000

# Initialize socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))
connection = client_socket.makefile('wb')

# Initialize Picamera2
camera = Picamera2()
camera.configure(camera.create_video_configuration(main={"size": (640, 480)}))
encoder = JpegEncoder(quality=Quality.MEDIUM)

camera.start()

try:
    while True:
        # Capture frame
        frame = camera.capture_array()
        # Serialize frame
        data = pickle.dumps(frame)
        # Pack message length and frame data
        message = struct.pack("Q", len(data)) + data
        # Send message
        connection.write(message)

except KeyboardInterrupt:
    pass

finally:
    # Release resources
    connection.close()
    client_socket.close()
    camera.stop()
