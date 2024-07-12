"""
Screwing around with HUD

@author  [Christopher Prol] [@prolvalone]

Date last modified: 07/12/2024
"""

import cv2 as cv
import numpy as np
import cvzone
#values for camera info
yAxisCam = 10
xAxisCam = 10

class testCam:
    def displayVideo():
        capture  = cv.VideoCapture(0)
        ret, frame = capture.read()
        hudTop = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/hudCompassHorizontal.png', cv.IMREAD_UNCHANGED)
        hudSide = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/hudCompassVertical.png', cv.IMREAD_UNCHANGED)
        
        hudTop = cv.resize(hudTop, (0, 0), None, 4, 4)
        hudSide = cv.resize(hudSide, (0, 0), None, 4, 4)
        topH, topW, topC = hudTop.shape
        hb, wb, cb = frame.shape
        sideH, sideW, sideC = hudSide.shape
        

        while True:
            ret, frame = capture.read()
            imgResult = cvzone.overlayPNG(frame, hudTop, [-250, -350])
            imgResult2 = cvzone.overlayPNG(imgResult, hudSide, [-350, -350])
            cv.imshow('TESTING HUD', imgResult2)
            if cv.waitKey(20) &0xFF == ord('q'):
                capture.release()
                cv.destroyWindow('TESTING HUD')




testCam.displayVideo()

