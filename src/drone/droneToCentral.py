'''
Code to send images from drone to central
from external camera mounted on the bottom

@author [Vito Tribuzio][Snoopy-0]

Date last modified: 06/16/2024
'''
import cv2 as cv
import base64
from gpiozero import Motor
from gpiozero import Servo
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import RPi.GPIO as GPIO

def transmitFeed(self):
        # # re-maps camera values and converts to bytearray
        # newTilt = self.numToRange(tiltPos, -1, 1, 0, 180)
        # newSwivel = self.numToRange(swivelPos, -1, 1, 0, 205)
        # newTele = self.numToRange(telePos, 0, 1, 0, 180) # figure out actual max
        # newZoom = self.numToRange(zoomPos, -1, 1, 0, 10)
        # cameraPos = [newTilt, newSwivel, newTele, newZoom]
        # cameraPosByte = bytearray(cameraPos)

        msg, clientAddr = self.videoSock.recvfrom(self.bufferSize)
        print('GOT connection from ', clientAddr)
        WIDTH = 400
        while True:
            buffer = self.picam2.capture_array("main")
            frame = cv.cvtColor(buffer, cv.COLOR_RGB2BGR)
            frame = cv.resize(frame, (WIDTH, int(WIDTH * frame.shape[1] / frame.shape[0])), interpolation=cv.INTER_AREA)
            print('Resized frame size:', frame.shape)

            encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

            message = base64.b64encode(buffer)
            #combined = cameraPosByte + message
            self.videoSock.sendto(message, clientAddr)
                
            cv.imshow('TRANSMITTING VIDEO', frame)
            key = cv.waitKey(1) & 0xFF
                
            if key == ord('q'):
                self.videoSock.close()
                self.picam2.stop()
                cv.destroyAllWindows()
                print('Server stopped by user')
                exit(0)