"""
Transmits rover video to central - - -  acts as server
Receives control code from central and transmits to arduino

@author [Zoe Rizzo] [@zizz-0]
        [Christopher Prol] [@prolvalone]
        [vito tribuzio] [@Snoopy-0]

Date last modified: 07/15/2024
"""
# Libraries
import cv2 as cv
import pickle
import socket
import base64
import time
import serial
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# Global variables
IP = '172.168.10.137'  # change to rover IP
PORT = 55555

# try:
#     arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
#     time.sleep(5)
#     print("Serial connection established")
# except serial.SerialException as e:
#     print(f"Error opening serial port {e}")
#     exit()


"""
Class for manipulation Rover Camera
"""
class Camera:
    def __init__(self):
        print("initializing")

    """
    Transmits Rover Video Data from a usb camera Over UDP sockets, acting as the server
    """
    def transmitUSBCamFeed():
        bufferSize = 65536
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        hostName = socket.gethostname()
        hostIp = socket.gethostbyname(hostName)
        print(hostIp)
        port = 9999
        socketAddress = (hostIp, port)
        serverSocket.bind(socketAddress)
        print('Listening at:', socketAddress)

        vid = cv.VideoCapture(0)
        cameraPos = bytearray(4)

        while True:
            # if arduino.in_waiting:
            #     arduino.readinto(cameraPos)  # bytearray

            msg, clientAddr = serverSocket.recvfrom(bufferSize)
            print('GOT connection from ', clientAddr)
            WIDTH = 400
            HEIGHT = 1080
            while vid.isOpened():
                _, frame = vid.read()
                frame = cv.resize(frame, (WIDTH, HEIGHT))
                encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

                message = base64.b64encode(buffer)
                combined = cameraPos + message
                serverSocket.sendto(combined, clientAddr)
                
                cv.imshow('TRANSMITTING VIDEO', frame)
                key = cv.waitKey(1) & 0xFF
                if key == ord('q'):
                    serverSocket.close()
                    break

    """
    Transmits camera feed from Picamera2 to Central via UDP sockets
    """
    def transmitPiCamFeed():
        bufferSize = 65536
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        hostName = socket.gethostname()
        hostIp = '192.168.110.255'  # socket.gethostbyname(hostName)
        print(hostIp)
        port = 9999
        socketAddress = (hostIp, port)
        serverSocket.bind(socketAddress)
        print('Listening at:', socketAddress)

        # Initialize Picamera2
        picam2 = Picamera2()
        videoConfig = picam2.create_video_configuration(main={"size": (640, 480)})
        picam2.configure(videoConfig)
        picam2.start()
        cameraPos = bytearray(4)

        while True:
            # if arduino.in_waiting:
            #     arduino.readinto(cameraPos)  # bytearray

            msg, clientAddr = serverSocket.recvfrom(bufferSize)
            print('GOT connection from ', clientAddr)
            WIDTH = 400
            while True:
                buffer = picam2.capture_array("main")
                frame = cv.cvtColor(buffer, cv.COLOR_RGB2BGR)
                frame = cv.resize(frame, (WIDTH, int(WIDTH * frame.shape[1] / frame.shape[0])), interpolation=cv.INTER_AREA)
                print('Resized frame size:', frame.shape)

                encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

                message = base64.b64encode(buffer)
                combined = cameraPos + message
                serverSocket.sendto(combined, clientAddr)
                
                cv.imshow('TRANSMITTING VIDEO', frame)
                key = cv.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    serverSocket.close()
                    picam2.stop()
                    cv.destroyAllWindows()
                    print('Server stopped by user')
                    exit(0)
                


"""
Class that defines a rover and its functionality
"""
class Rover:
    """
    Initializes an instance of Rover 
    """
    def __init__(self):
        self.loopCount = 0
        self.control = 0  # control state -- even => central, odd => drone
        self.on = True  # Rover running

        # UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((IP, PORT))

    """
    Starts the rover and runs the drive loop
    @param `maxLoopCount` : how many loops to wait through in the event of an extended period of no controls transmitted
    """
    def start(self, maxLoopCount=1):
        print("Starting rover...")

        while self.on:
            self.drive()
            # If no commands are sent for an extended period of time
            if self.loopCount > maxLoopCount:
                self.on = False

    """
    Main drive loop
    Will receive controller input from central and transmit to arduino
    """
    def drive(self):
        while self.on:
            serializedControls, addr = self.sock.recvfrom(1024)
            controls = pickle.loads(serializedControls)  # unserializes controls
            inputCtrls = ",".join(f"{key}:{value}" for key, value in controls.items())  # turns serialized controls from dict to string
            print(inputCtrls)
            # arduino.write((inputCtrls + '\n').encode())
            # print("Sent to Arduino: ", inputCtrls)

            # if arduino.in_waiting > 0:
            #     line = arduino.readline().decode('utf-8').rstrip()
            #     print(line)


rover = Rover()
rover.start()

# cam = Camera
# cam.transmitUSBCamFeed()
