"""
Screwing around with HUD

@author  [Christopher Prol] [@prolvalone]

Date last modified: 07/12/2024
"""
import cv2 as cv
import numpy as np
#values for camera info
yAxisCam = 10
xAxisCam = 10

class testCam:
    def displayVideo():
        capture  = cv.VideoCapture(0)
        hudTop = cv.imread('assets/hudCompassHorizontal.png')
        hudSide = cv.imread('assets/hudCompassVertical.png')
        #hudTop = cv.resize(hudTop, (100,100))
        




        while True:
            isTrue, frame = capture.read()
            cv.imshow('TESTING HUD', frame)
            if cv.waitKey(20) &0xFF == ord('q'):
                capture.release()
                cv.destroyWindow('TESTING HUD')




testCam.displayVideo()