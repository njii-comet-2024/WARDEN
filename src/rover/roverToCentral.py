"""
Transmits rover video to central - - -  acts as server

@author [Zoe Rizzo] [@zizz-0]
        [Christopher Prol] [@prolvalone]
        [vito tribuzio] [@Snoopy-0]
        [Soumya Khera] [@soumya-khera]

Date last modified: 07/17/2024
"""
# Libraries
import cv2 as cv
import socket
import base64
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# Global variables
IP = '192.168.110.78'  # change to camera pi IP
SEND_PORT = 9999
RECV_PORT = 1111

"""
Class for manipulation Rover Camera
"""
class Camera:
    def __init__(self):
        print("Initializing...")

        # Socket to send video feed to central pi
        self.bufferSize = 65536
        self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bufferSize)
        hostName = socket.gethostname()
        hostIp = socket.gethostbyname(hostName)
        socketAddress = (hostIp, SEND_PORT)
        self.sendSocket.bind(socketAddress)
        print('Listening at: ', socketAddress)

        # Socket to receive camera pos from controls pi
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvSocket.bind((IP, RECV_PORT))

    """
    Transmits Rover Video Data from a usb camera Over UDP sockets, acting as the server
    """
    def transmitUSBCamFeed(self):
        vid = cv.VideoCapture(0)

        while True:
            msg, clientAddr = self.sendSocket.recvfrom(self.bufferSize)
            print('GOT connection from ', clientAddr)

            cameraPos, addr = self.recvSocket.recvfrom(1024) # recv camera pos from controls pi

            WIDTH = 1080
            HEIGHT = 400
            while vid.isOpened():
                
                _, frame = vid.read()
                frame = cv.resize(frame, (WIDTH, HEIGHT))
                encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

                message = base64.b64encode(buffer)
                combined = cameraPos + message
                self.sendSocket.sendto(combined, clientAddr)
                
                cv.imshow('TRANSMITTING VIDEO', frame)
                key = cv.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.sendSocket.close()
                    break

    """
    Transmits camera feed from Picamera2 to Central via UDP sockets
    """
    def transmitPiCamFeed(self):
        # Initialize Picamera2
        picam2 = Picamera2()
        videoConfig = picam2.create_video_configuration(main={"size": (1080, 400)})
        picam2.configure(videoConfig)
        picam2.start()

        while True:
            msg, clientAddr = self.sendSocket.recvfrom(self.bufferSize)
            print('GOT connection from ', clientAddr)
            
            cameraPos, addr = self.recvSocket.recvfrom(1024) # recv camera pos from controls pi

            WIDTH = 400
            while True:
                buffer = picam2.capture_array("main")
                frame = cv.cvtColor(buffer, cv.COLOR_RGB2BGR)
                frame = cv.resize(frame, (1080, 400 ), interpolation=cv.INTER_AREA)
                print('Resized frame size:', frame.shape)

                encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

                message = base64.b64encode(buffer)
                combined = cameraPos + message
                self.sendSocket.sendto(combined, clientAddr)
                
                cv.imshow('TRANSMITTING VIDEO', frame)
                key = cv.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    self.sendSocket.close()
                    picam2.stop()
                    cv.destroyAllWindows()
                    print('Server stopped by user')
                    exit(0)