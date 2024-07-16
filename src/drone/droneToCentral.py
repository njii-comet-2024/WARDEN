'''
code to send images from drone to central
from external camera mounted on the bottom

    @author [Vito Tribuzio][Snoopy-0]

date last modified: 06/16/2024
'''

#imports
import cv2
import numpy as np
import socket
import pickle
import struct

#initializing connection variables
centralIP = '192.168.110.5' #placeholder ip
port = 55555

#initializing camera variable
camera = cv2.VideoCapture(0) #0 = device index
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((centralIP, port))

while True:
    ret, frame = camera.read()
    data = pickle.dumps(frame)

    messageSize = struct.pack("L", len(data))

    s.sendall(messageSize + data)
