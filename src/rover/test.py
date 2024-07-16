"""
TEST FILE TO SIMULTANEOUSLY RECEIVE CONTROLS AND SEND VIDEO
"""
# Libraries
import cv2 as cv
import pickle
import socket
import base64

# Global variables
IP = '172.168.10.136'  # change to rover IP
VIDEO_PORT = 9999
CONTROLS_PORT = 55555

cameraType = 0

rightSpeed = 0
leftSpeed = 0

# Servo range => (-1, 1)
tiltPos = 0
swivelPos = 0
zoomPos = 0
telePos = 0 # change to middle position

"""
Class that defines a rover and its functionality
Receives drive controls, runs them on rover, and transmits video feed and camera positions back to central
"""
class Rover:
    def __init__(self):
        print("Initializing...")
        self.on = True  # Rover running

        # UDP
        self.bufferSize = 65536
        self.controlSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.controlSock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bufferSize)
        self.controlSock.bind((IP, CONTROLS_PORT))

        self.videoSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.videoSock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.bufferSize)
        self.videoSock.bind((IP, VIDEO_PORT))
    
    """
    Maps a number from one range to another
    @param `num` : number to re-map
    @param `inMin` : original range min
    @param `inMax` : original range max
    @param `outMin` : target range min
    @param `outMax` : target range max
    """
    def numToRange(num, inMin, inMax, outMin, outMax):
        return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax
                        - outMin))
    
    """
    Starts the rover and runs the transmission and drive loops
    THERE IS A CHANCE THIS DOES NOT WORK -- TEST TO SEE IF SEPARATING INTO HELPER CLASSES CAUSES LAG
    """
    def start(self):
        print("Rover starting...")
        while self.on:
            self.transmitUSBCamFeed()
            self.drive()

    """
    Transmits Rover Video Data from a usb camera Over UDP sockets, acting as the server
    FOR TESTING ONLY
    """
    def transmitUSBCamFeed(self):
        vid = cv.VideoCapture(0)

        while True:
            # re-maps camera values and converts to bytearray
            # newTilt = self.numToRange(tiltPos, -1, 1, 0, 180)
            # newSwivel = self.numToRange(swivelPos, -1, 1, 0, 205)
            # newTele = self.numToRange(telePos, 0, 1, 0, 180) # figure out actual max
            # newZoom = self.numToRange(zoomPos, -1, 1, 0, 10)
            # cameraPos = [newTilt, newSwivel, newTele, newZoom]
            cameraPos = [tiltPos, swivelPos, telePos, zoomPos]
            cameraPosByte = bytearray(cameraPos)

            msg, clientAddr = self.videoSock.recvfrom(self.bufferSize)
            print('GOT connection from ', clientAddr)
            WIDTH = 400
            HEIGHT = 1080
            while vid.isOpened():
                _, frame = vid.read()
                frame = cv.resize(frame, (WIDTH, HEIGHT))
                encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

                message = base64.b64encode(buffer)
                combined = cameraPosByte + message
                self.videoSock.sendto(combined, clientAddr)
                
                cv.imshow('TRANSMITTING VIDEO', frame)
                key = cv.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.videoSock.close()
                    break
    
    """
    Main drive loop
    Will receive controller input from central and run controls on rover
    """
    def drive(self):
        ctrls = []
        serializedControls, addr = self.controlSock.recvfrom(1024)
        controls = pickle.loads(serializedControls)  # unserializes controls

        if(controls["leftTread"] > 0):
            ctrls.append("Left fwd")

        if(controls["rightTread"] < 0):
            ctrls.append("Left back")

        if(controls["rightTread"] > 0):
            ctrls.append("Right fwd")

        if(controls["rightTread"] < 0):
            ctrls.append("Right back")

        # not fully sure about PUL pins or ENA pins (some online code says LOW to enable but some says HIGH)
        if(controls["leftWheg"] > 0):
            ctrls.append("Left wheg up")

        if(controls["leftWheg"] < 0):
            ctrls.append("Left wheg down")
        
        if(controls["rightWheg"] > 0):
            ctrls.append("Right wheg up")

        if(controls["rightWheg"] < 0):
            ctrls.append("Right wheg down")

        if(controls["cameraTypeToggle"] > 0):
            ctrls.append("[OBSOLETE]")

        if(controls["cameraTelescope"] > 0):
            # find max
            # if telePos < max
            telePos += 1
            ctrls.append("Telescope up")
        
        if(controls["cameraTelescope"] < 0):
            if(telePos > 0):
                telePos -= 1
                ctrls.append("Telescope down")

        if(controls["cameraTilt"] > 0):
            if(tiltPos < 1):
                tiltPos += 0.05
                ctrls.append("Tilt up")
        
        if(controls["cameraTilt"] < 0):
            if(tiltPos > -1):
                tiltPos -= 0.05
                ctrls.append("Tilt down")

        if(controls["cameraLeft"] > 0):
            if(swivelPos > -1):
                swivelPos -= 0.05
                ctrls.append("Swivel left")
        
        if(controls["cameraRight"] > 0):
            if(swivelPos < 1):
                swivelPos += 0.05
                ctrls.append("Swivel right")
        
        if(controls["cameraZoom"] > 0):
            if(zoomPos < 1):
                zoomPos += 0.5
                ctrls.append("Zoom in")

        if(controls["cameraZoom"] < 0):
            if(zoomPos > -1):
                zoomPos -= 0.5
                ctrls.append("Zoom out")
        
        if(ctrls):
            print(ctrls)

rover = Rover()
rover.start()