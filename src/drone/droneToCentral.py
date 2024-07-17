'''
Code to send images from drone to central
from external camera mounted on the bottom

@author [Vito Tribuzio][Snoopy-0]

Date last modified: 06/16/2024
'''
import cv2 as cv
import base64
from picamera2 import Picamera2
import socket

class DroneTransmitter:
    def __init__(self, bufferSize=65536, width=400):
        self.bufferSize = bufferSize
        self.width = width
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_still_configuration())
        self.picam2.start()
        self.videoSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def transmitFeed(self):
        msg, clientAddr = self.videoSock.recvfrom(self.bufferSize)
        print('GOT connection from ', clientAddr)
        
        while True:
            buffer = self.picam2.capture_array("main")
            frame = cv.cvtColor(buffer, cv.COLOR_RGB2BGR)
            frame = cv.resize(frame, (self.width, int(self.width * frame.shape[1] / frame.shape[0])), interpolation=cv.INTER_AREA)
            print('Resized frame size:', frame.shape)

            encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])
            message = base64.b64encode(buffer)

            self.videoSock.sendto(message, clientAddr)
                
            cv.imshow('TRANSMITTING VIDEO', frame)
            key = cv.waitKey(1) & 0xFF
                
            if key == ord('q'):
                self.videoSock.close()
                self.picam2.stop()
                cv.destroyAllWindows()
                print('Server stopped by user')
                exit(0)

if __name__ == "__main__":
    drone = DroneTransmitter()
    drone.transmitFeed()
