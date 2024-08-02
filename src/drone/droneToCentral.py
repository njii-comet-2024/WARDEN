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

# Socket parameters
server_ip = '192.168.110.5'  # Replace with receiver's IP address
server_port = 5005

# Initialize socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))
connection = client_socket.makefile('wb')

# Initialize Picamera2
camera = Picamera2()
camera_config = camera.create_still_configuration(main={"size": (1024, 600)}, lores={"size": (1024, 600)}, display="lores")
camera.configure(camera_config)
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
    client_socket.close()
    camera.stop()
