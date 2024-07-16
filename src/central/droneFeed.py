"""
sets up server for all vehicles to connect too - - - acts as client
@author [Vito Tribuzio][@Snoopy-0]

Date last modified: 07/15/2024
"""

# Libraries
import socket
import cv2 as cv
import numpy as np 
import base64
import struct
import pickle

#initial capture
#capture  = cv.VideoCapture(0)
#ret, frame = capture.read()

DRONE_IP = '192.168.110.19'
PORT = 55555

#sets up the server as well as sends the camera feed to the central server
def serverSetup():
    #create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #reserved a port on computer, can be anything
    port = 55555

    #bind to the port, no ip in ip field which makes server listen to request
    s.bind(('', port))
    print ("socket binded to %s" %(port))

    #put socket into listening mode
    s.listen(5)
    print ("socket is listening")

    #accept new connection
    c, addr = s.accept()
    print ('Got connection from', addr)

    data = input(' -> ')

    data = b''
    payloadSize = struct.calcsize("L")

    while True:
            # Retrieve message size
            while len(data) < payloadSize:
                packet = c.recv(4096)
                if not packet:
                    break
                data += packet

            if len(data) < payloadSize:
                break

            packedMessageSize = data[:payloadSize]
            data = data[payloadSize:]
            messageSize = struct.unpack("L", packedMessageSize)[0]

        # Retrieve all data based on message size
            while len(data) < messageSize:
                data += c.recv(4096)

            frameData = data[:messageSize]
            data = data[messageSize:]

            frame = pickle.loads(frameData)

            cv.imshow('frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

    c.close()
    cv.destroyAllWindows()

serverSetup()