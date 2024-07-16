"""
Client Side Video testing

@author  [Christopher Prol] [@prolvalone]

Date last modified: 07/16/2024
"""
import cv2 as cv
import socket 
import cvzone
import numpy as np
import base64

ROVER_IP = '172.168.10.137'
TOP_HORIZ = -300
TOP_VERT = -340
SIDE_VERT = -370
SIDE_HORIZ = -340


class videoReciever:
    def __init__(self):
        print("initializing")


    """
    This function recieves Rover Cam footage from the PI Camera.  
    """
    def recieveRoverCam(roverIP):
        #initiate Window and resize
        cv.namedWindow('TESTING HUD', cv.WINDOW_NORMAL)
        cv.resizeWindow('TESTING HUD', 1024, 600)
        #socket information
        bufferSize = 65536
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        print(roverIP)
        port = 9999                                 # can change based on possible interference, etc
        message = b'Hello'                          # test message
       
        #connect to server socket
        clientSocket.sendto(message, (roverIP,port))

        #read the image files
        hudTop = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/hudCompassHorizontal.png', cv.IMREAD_UNCHANGED)
        hudSide = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/hudCompassVertical.png', cv.IMREAD_UNCHANGED)
        hudTopIndicator = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/arrow.png', cv.IMREAD_UNCHANGED)
        hudSideIndicator = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/arrow.png', cv.IMREAD_UNCHANGED)
        hudHeightIndicator = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/arrowRed.png', cv.IMREAD_UNCHANGED)

        #rotate and resize images to be properly aligned
        hudTop = cv.rotate(hudTop, cv.ROTATE_180)
        hudTop = cv.resize(hudTop, (0, 0), None, 5.8, 3.95)
        hudSide = cv.rotate(hudSide, cv.ROTATE_180)
        hudSide = cv.resize(hudSide, (0, 0), None, 4, 4)
        hudSideIndicator = cv.rotate(hudSideIndicator, cv.ROTATE_90_COUNTERCLOCKWISE)
        hudSideIndicator = cv.resize(hudSideIndicator, (0,0), None, .1, .1)
        hudTopIndicator = cv.resize(hudTopIndicator, (0, 0), None, .1, .1)
        hudHeightIndicator = cv.resize(hudHeightIndicator, (0, 0), None, .4, .1)
        #loop for displaying video
        while True:
            #recieve Packet
            packet,_ = clientSocket.recvfrom(bufferSize)
            #interpret packet
            cameraPosLength = 4
            cameraPos = packet[:cameraPosLength]
            imgData = packet[4:]
            #decode data
            data = base64.b64decode(imgData, ' /')
            npdata = np.fromstring(data, dtype=np.uint8)
            frame = cv.imdecode(npdata, 1)
            #adds indicator bars to HUD
            imgResult = cvzone.overlayPNG(frame, hudTop, [TOP_HORIZ, TOP_VERT]) # adds top Hud
            imgResult = cvzone.overlayPNG(imgResult, hudSide, [SIDE_HORIZ, SIDE_VERT]) #adds side hud
            #create positional data variables
            cameraPosData = [int(b) for b in cameraPos]
            cameraHeight = cameraPosData[0]
            cameraTilt = cameraPosData[1]
            cameraRotation = cameraPosData[2]
            cameraZoom = cameraPosData[3]
            print(cameraPosData)

            #display location coords
            imgResult = cv.putText(imgResult,'Height: ' + str(cameraHeight) + ' Zoom: ' + str(cameraZoom) + 'x', (10, 360), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0),2)
            imgResult = cv.putText(imgResult, 'ValueY: ' + str(cameraTilt) + '  ValueX: ' + str(cameraRotation), (10, 380), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0),2)
            #display max limit messages
            if(cameraTilt == 0 or cameraTilt == 180):
                imgResult = cv.putText(imgResult, 'Y AXIS LIMIT REACHED' , (390, 380), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255),2)
            if(cameraRotation == 0 or cameraRotation == 205):
                imgResult = cv.putText(imgResult, 'X AXIS LIMIT REACHED' , (390, 350), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255),2)
            if(cameraHeight == 0 or cameraHeight == 180):
                imgResult = cv.putText(imgResult, 'HEIGHT LIMIT REACHED' , (650, 350), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255),2)
            if(cameraZoom == 0 or cameraZoom == 10):
                imgResult = cv.putText(imgResult, 'ZOOM LIMIT REACHED' , (650, 380), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255),2)
            #overlay indicator
            imgResult = cvzone.overlayPNG(imgResult, hudTopIndicator, [cameraRotation * 5, TOP_VERT + 350])#adds moving vertical
            imgResult = cvzone.overlayPNG(imgResult, hudSideIndicator, [SIDE_HORIZ + 350, cameraTilt * 2])
            imgResult = cvzone.overlayPNG(imgResult, hudHeightIndicator, [960, cameraHeight * 2])
            #display video
            cv.imshow('TESTING HUD', frame)

            #exit key
            if cv.waitKey(20) &0xFF == ord('q'):
                cv.destroyAllWindows()
                break

#serverProgram()
videoReciever.recieveRoverCam(ROVER_IP)