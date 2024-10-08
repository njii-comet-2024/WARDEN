"""
Screwing around with HUD

@author  [Christopher Prol] [@prolvalone]

Date last modified: 07/15/2024
"""

import cv2 as cv
import cvzone
#values for camera info


#values for stationary overlays
TOP_HORIZ = -85
TOP_VERT = 0
SIDE_VERT = -160
SIDE_HORIZ = -2
SIDE_ACTU = 340
#values for moving overlawys



class testCam:
    """
    Test code for getting the HUD display on the video

    definitely need a abetter image for the compass
    """
    def displayVideo():
        #variables
        yAxisCam = 0
        xAxisCam = 50
        actuatorHeight = 40
        dirValY = 1
        dirValX = 1
        dirValActuator = 1
        


        #initial capture
        capture  = cv.VideoCapture(0)
        ret, frame = capture.read()
        #read the image files    - - - - will need to be edited once on pi
        hudTop = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/hudCompassHorizontal.png', cv.IMREAD_UNCHANGED)
        hudSide = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/hudCompassHorizontal.png', cv.IMREAD_UNCHANGED)
        hudTopIndicator = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/arrow.png', cv.IMREAD_UNCHANGED)
        hudSideIndicator = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/arrow.png', cv.IMREAD_UNCHANGED)
        actuatorIndicator = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/arrowRed.png', cv.IMREAD_UNCHANGED)
        #rotate and resize
        hudTop = cv.rotate(hudTop, cv.ROTATE_180)
        hudSide = cv.rotate(hudSide, cv.ROTATE_90_CLOCKWISE)
        hudSideIndicator = cv.rotate(hudSideIndicator, cv.ROTATE_90_COUNTERCLOCKWISE)
        hudTop = cv.resize(hudTop, (0, 0), None, 1, 1)
        hudSide = cv.resize(hudSide, (0, 0), None, 1, 1)
        hudTopIndicator = cv.resize(hudTopIndicator, (0, 0), None, .1, .1)
        hudSideIndicator = cv.resize(hudSideIndicator, (0,0), None, .1, .1)
        actuatorIndicator = cv.resize(actuatorIndicator, (0,0), None, .1, .1)
        while True:
            #DELETE FROM HERE TO NEXT COMMENT ONCE INTEGRATED
            #This is a placeholder for the SERVO input
            
            yAxisCam += dirValY
            xAxisCam += dirValX
            dirValActuator += dirValActuator
            if(yAxisCam >= 210 or yAxisCam <= 0):
                dirValY *= -1
            if(xAxisCam >= 200 or xAxisCam <= 0):
                dirValX *= -1
            if(actuatorHeight >=200 or actuatorHeight <=0):
                dirValActuator *=1
            
            
            #DELETE ABOVE THIS

            #capture
            ret, frame = capture.read()
            #overlay satic gui parts
            imgResult = cvzone.overlayPNG(frame, hudTop, [TOP_HORIZ, TOP_VERT]) # adds top Hud
            imgResult = cvzone.overlayPNG(imgResult, hudSide, [SIDE_HORIZ, SIDE_VERT]) #adds side hud
            imgResult = cvzone.overlayPNG(imgResult, actuatorIndicator, [SIDE_ACTU, SIDE_VERT]) #adds actuator arrow
            #display location coords
            imgResult = cv.putText(imgResult, 'ValueY: ' + str(yAxisCam) + '  ValueX: ' + str(xAxisCam), (10, 460), cv.FONT_HERSHEY_COMPLEX, 0.6, (255,0,0),2)
            #display max limit messages
            if(yAxisCam == 0 or yAxisCam == 180):
                imgResult = cv.putText(imgResult, 'Y AXIS LIMIT REACHED' , (410, 420), cv.FONT_HERSHEY_COMPLEX, 0.6, (0,0,255),2)
            
            if(xAxisCam == 0 or xAxisCam == 180):
                imgResult = cv.putText(imgResult, 'X AXIS LIMIT REACHED' , (410, 460), cv.FONT_HERSHEY_COMPLEX, 0.6, (0,0,255),2)
            #overlay indicator
            imgResult = cvzone.overlayPNG(imgResult, hudTopIndicator, [xAxisCam * 3, TOP_VERT])#adds moving vertical
            imgResult = cvzone.overlayPNG(imgResult, hudSideIndicator, [SIDE_HORIZ, yAxisCam * 2])
            cv.namedWindow('TESTING HUD', cv.WINDOW_NORMAL)
            cv.imshow('TESTING HUD', imgResult)
            cv.resizeWindow('TESTING HUD', 1024, 600)
            if cv.waitKey(20) &0xFF == ord('q'):
                capture.release()
                cv.destroyWindow('TESTING HUD')




testCam.displayVideo()

