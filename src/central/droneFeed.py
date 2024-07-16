"""
Sets up server for all vehicles to connect to - - - acts as client
@author [Vito Tribuzio][@Snoopy-0]

Date last modified: 07/15/2024
"""

# Libraries
import socket
import cv2 as cv
import numpy as np 
import struct
import pickle

PORT = 55555

# Sets up the server as well as sends the camera feed to the central server
def serverSetup():
    # Create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind to the port, no IP in IP field which makes server listen to requests
    s.bind(('', PORT))
    print(f"Socket binded to {PORT}")

    # Put socket into listening mode
    s.listen(5)
    print("Socket is listening")

    # Accept new connection
    c, addr = s.accept()
    print('Got connection from', addr)

    data = b''
    payload_size = struct.calcsize("L")

    while True:
        # Retrieve message size
        while len(data) < payload_size:
            packet = c.recv(4096)
            if not packet:
                break
            data += packet

        if len(data) < payload_size:
            break

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]

        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += c.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data)

        cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    c.close()
    cv.destroyAllWindows()

serverSetup()
