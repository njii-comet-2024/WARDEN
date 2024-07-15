"""
Transmits rover video to central
Receives control code from central and transmits to arduino

@author [Zoe Rizzo] [@zizz-0]
        [Christopher Prol] [@prolvalone]
        [vito tribuzio] [@Snoopy-0]

Date last modified: 07/11/2024
"""
# Libraries
import cv2 as cv
import pickle
import socket
import numpy as np
import base64
import time
import serial
import imutils
from picamera.array import PiRGBArray
from picamera import PiCamera


# Global variables
ROVER_IP = '172.168.10.137' # delete later and use `IP`

IP = '172.168.10.137' # change to rover IP
PORT = 55555

#arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1) added function for connection to allow for easier use
#time.sleep(2)  # Allow some time for the Arduino to reset

try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(5)
    print("Serial connection established")
except serial.SerialException as e:
    print(f"Error opening serial port {e}")
    exit()

# s = socket.socket() # TCP

"""
Class for manipulation Rover Camera
"""
class Camera:
    def __init__(self):
        print("initializing")

    """
    This function recieves rover camera feed
    
    this is probably unnecessary given transmitRoverFeed 
    function
    """
    def getRoverFeed():
        capture = cv.VideoCapture(1) # need origin of camera, 2 potentially works, potentially doesnt
        
        while True:
            isTrue, frame = capture.read()
            cv.imshow('frame', frame)
            if cv.waitKey(20) & 0xFF ==ord('q'):
                break

        capture.release()

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
        socketAddress = (hostIp,port)
        serverSocket.bind(socketAddress)
        print('Listening at:', socketAddress)

        vid = cv.VideoCapture(0) #  replace 'rocket.mp4' with 0 for webcam
        fps, st, framesToCount, cnt = (0,0,20,0)
        cameraPos = bytearray(4)

        while True:
            if arduino.in_waiting():
                arduino.readinto(cameraPos) # bytearray

            msg,clientAddr = serverSocket.recvfrom(bufferSize)
            print('GOT connection from ', clientAddr)
            WIDTH=400
            while(vid.isOpened()):
                _,frame = vid.read()
                # frame = cv.resize(frame, (WIDTH, -1), fx=1.0, fy=None)
                frame = imutils.resize(frame, width=WIDTH)
                encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY,80])

                message = base64.b64encode(buffer)
                combined = cameraPos + message
                serverSocket.sendto(combined,clientAddr)
                
                frame = cv.putText(frame, 'FPS: '+str(fps), (10,40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
                cv.imshow('TRANSMITTING VIDEO', frame)
                key = cv.waitKey(1) & 0xFF
                if key == ord('q'):
                    serverSocket.close()
                    break
                if cnt == framesToCount:
                    try:
                        fps = round(framesToCount/(time.time()-st))
                        st=time.time()
                        cnt=0
                    except:
                        pass
                cnt+=1
        
    """
    Transmits camera feed from PICAMERA to Central via UDP sockets
    """
    def transmitPiCamFeed():
        bufferSize = 65536
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        hostName = socket.gethostname()
        hostIp = '192.168.110.255'# socket.gethostbyname(hostName)
        print(hostIp)
        port = 9999
        socketAddress = (hostIp, port)
        serverSocket.bind(socketAddress)
        print('Listening at:', socketAddress)

        # Initialize PiCamera
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 30
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.1)

        fps, st, framesToCount, cnt = (0, 0, 20, 0)
        cameraPos = bytearray(4)

        while True:
            if arduino.in_waiting():
                arduino.readinto(cameraPos) # bytearray

            msg, clientAddr = serverSocket.recvfrom(bufferSize)
            print('GOT connection from ', clientAddr)
            WIDTH = 400
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                image = frame.array
                print('Captured frame size:', image.shape)
                image = cv.resize(image, (WIDTH, int(WIDTH * image.shape[1] / image.shape[0])), interpolation=cv.INTER_AREA)
                print('Resized frame size:', image.shape)

                encoded, buffer = cv.imencode('.jpg', image, [cv.IMWRITE_JPEG_QUALITY, 80])

                message = base64.b64encode(buffer)
                combined = cameraPos + message
                serverSocket.sendto(combined,clientAddr)
                
                image = cv.putText(image, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv.imshow('TRANSMITTING VIDEO', image)
                key = cv.waitKey(1) & 0xFF
                rawCapture.truncate(0)
                
                if key == ord('q'):
                    serverSocket.close()
                    camera.close()
                    cv.destroyAllWindows()
                    print('Server stopped by user')
                    exit(0)
                
                if cnt == framesToCount:
                    fps = round(framesToCount / (time.time() - st))
                    st = time.time()
                    cnt = 0
                
                cnt += 1

"""
Class that defines a rover and its functionality
"""
class Rover:
    """
    Initializes an instance of Rover 
    """
    def __init__(self):
        self.loopCount = 0
        self.control = 0 # control state -- even => central, odd => drone
        self.on = True # Rover running

        # UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((IP, PORT))

        # TCP
        # s.connect((CENTRAL_IP, port))

    """
    Starts the rover and runs the drive loop
    @param `maxLoopCount` : how many loops to wait through in the event of an extended period of no controls transmitted
    """
    def start(self, maxLoopCount=1):
        print("Starting rover...")

        while self.on:
            self.drive()
            # If no commands are sent for an extended period of time
            if(self.loopCount > maxLoopCount):
                self.on = False

    """
    Main drive loop
    Will receive controller input from central and transmit to arduino
    """
    def drive(self):
        while self.on:
            serializedControls, addr = self.sock.recvfrom(1024)
            controls = pickle.loads(serializedControls) # unserializes controls
            inputCtrls = ",".join(f"{key}:{value}" for key, value in controls.items()) # turns serialized controls from dict to string
            arduino.write((inputCtrls + '\n').encode())
            print("Sent to Arduino: ", inputCtrls)

# rover = Rover()
# rover.start()

cam = Camera
cam.transmitUSBCamFeed()