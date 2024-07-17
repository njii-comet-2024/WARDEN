"""
Sets up server for all vehicles to connect to - - - acts as client
@author [Vito Tribuzio][@Snoopy-0]

Date last modified: 07/15/2024
"""
import cv2 as cv
import socket
import numpy as np
import base64

DRONE_IP = '192.168.110.19'
PORT = 22222
BUFFER_SIZE = 65536

class VideoReceiver:
    def __init__(self, drone_ip, port, buffer_size):
        self.drone_ip = drone_ip
        self.port = port
        self.buffer_size = buffer_size
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)

    def receiveDroneCam(self):
        message = b'Hello'
        self.clientSocket.sendto(message, (self.drone_ip, self.port))

        while True:
            packet, _ = self.clientSocket.recvfrom(self.buffer_size)
            imgData = packet

            data = base64.b64decode(imgData)
            npdata = np.frombuffer(data, dtype=np.uint8)
            frame = cv.imdecode(npdata, 1)

            cv.imshow('TESTING HUD', frame)

            if cv.waitKey(20) & 0xFF == ord('q'):
                cv.destroyAllWindows()
                break

if __name__ == "__main__":
    receiver = VideoReceiver(DRONE_IP, PORT, BUFFER_SIZE)
    receiver.receiveDroneCam()
