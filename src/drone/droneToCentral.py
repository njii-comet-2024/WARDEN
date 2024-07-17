'''
Code to send images from drone to central
from external camera mounted on the bottom

@author [Vito Tribuzio][Snoopy-0]

Date last modified: 06/16/2024
'''
import cv2
import socket
import struct
import pickle

# Socket parameters
server_ip = 'RECEIVER_IP_ADDRESS'  # Replace with receiver's IP address
server_port = 5000

# Initialize socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))
connection = client_socket.makefile('wb')

# Initialize video capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Serialize frame
    data = pickle.dumps(frame)
    # Pack message length and frame data
    message = struct.pack("Q", len(data)) + data

    # Send message
    connection.write(message)

# Release resources
cap.release()
connection.close()
client_socket.close()
