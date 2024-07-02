"""
Receives video feed from rover

@author [Christopher Prol] [prolvalone]

Date last modified: 07/02/2024
"""

# Libraries
import cv2 as cv
import pickle
import struct



class Camera:

    def __init__(self):
        print("initializing")

    def getRoverFeed():
        """
        This function recieves rover camera feed
        """
        capture = cv.VideoCapture(1) # need origin of camera, 2 potentially works, potentially doesnt
        
        while True:
            isTrue, frame = capture.read()
            cv.imshow('frame', frame)
            if cv.waitKey(20) & 0xFF ==ord('q'):
                break

        capture.release()

Camera.getRoverFeed()

