'''
Code to send images from drone to central
from external camera mounted on the bottom

@author [Vito Tribuzio][Snoopy-0]

Date last modified: 06/16/2024
'''

# Imports
import cv2
import numpy as np
import socket
import pickle
import struct

# Initializing connection variables
centralIP = '192.168.110.5'  # Placeholder IP
port = 55555

# Initializing camera variable
camera = cv2.VideoCapture(0)  # 0 = device index
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((centralIP, port))

while True:
    ret, frame = camera.read()
    if not ret:
        continue

    data = pickle.dumps(frame)
    message_size = struct.pack("L", len(data))

    s.sendall(message_size + data)
