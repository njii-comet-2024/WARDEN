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
TOP_HORIZ = -293
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
        #camera locations
        yAxisCam = 0
        xAxisCam = 50
        dirValY = 1
        dirValX = 1
        #socket information
        bufferSize = 65536
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
       # hostName = socket.gethostname() - - - - unused with pass of roverIP
        print(roverIP)
        port = 9999                                 # can change based on possible interference, etc
        message = b'Hello'                          # test message
       
        #read the image files
        hudTop = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/hudCompassHorizontal.png', cv.IMREAD_UNCHANGED)
        hudSide = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/hudCompassVertical.png', cv.IMREAD_UNCHANGED)
        hudTopIndicator = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/arrow.png', cv.IMREAD_UNCHANGED)
        hudSideIndicator = cv.imread('/Users/chris/OneDrive/Desktop/testingPe/arrow.png', cv.IMREAD_UNCHANGED)

        #connect to server socket
        clientSocket.sendto(message, (roverIP,port))

        #rotate and resize images to be properly aligned
        hudTop = cv.rotate(hudTop, cv.ROTATE_180)
        hudTop = cv.resize(hudTop, (0, 0), None, 4, 4)
        hudSide = cv.rotate(hudSide, cv.ROTATE_180)
        hudSide = cv.resize(hudSide, (0, 0), None, 4, 4)
        hudSideIndicator = cv.rotate(hudSideIndicator, cv.ROTATE_90_COUNTERCLOCKWISE)
        hudSideIndicator = cv.resize(hudSideIndicator, (0,0), None, .1, .1)
        hudTopIndicator = cv.resize(hudTopIndicator, (0, 0), None, .1, .1)

        #loop for displaying video
        while True:
            #DELETE FROM HERE TO NEXT COMMENT ONCE INTEGRATED
            #This is a placeholder for the SERVO input
            
            yAxisCam += dirValY
            xAxisCam += dirValX
            if(yAxisCam >= 210 or yAxisCam <= 0):
                dirValY *= -1
            if(xAxisCam >= 200 or xAxisCam <= 0):
                dirValX *= -1
            
            
            #DELETE ABOVE THIS
           
            #recieve Packet
            packet,_ = clientSocket.recvfrom(bufferSize)

            cameraPosLength = 4
            cameraPos = packet[:cameraPosLength]
            imgData = packet[cameraPosLength:]

            data = base64.b64decode(imgData, ' /')
            npdata = np.fromstring(data, dtype=np.uint8)
            frame = cv.imdecode(npdata, 1)
            imgResult = cvzone.overlayPNG(frame, hudTop, [TOP_HORIZ, TOP_VERT]) # adds top Hud
            imgResult = cvzone.overlayPNG(imgResult, hudSide, [SIDE_HORIZ, SIDE_VERT]) #adds side hud

            cameraPosData = [float(b) for b in cameraPos]
            print(cameraPosData)
            #display location coords
            imgResult = cv.putText(imgResult, 'ValueY: ' + str(yAxisCam) + '  ValueX: ' + str(xAxisCam), (10, 460), cv.FONT_HERSHEY_COMPLEX, 0.6, (255,0,0),2)
            #display max limit messages
            if(yAxisCam == 0 or yAxisCam == 180):
                imgResult = cv.putText(imgResult, 'Y AXIS LIMIT REACHED' , (410, 420), cv.FONT_HERSHEY_COMPLEX, 0.6, (0,0,255),2)
            
            if(xAxisCam == 0 or xAxisCam == 180):
                imgResult = cv.putText(imgResult, 'X AXIS LIMIT REACHED' , (410, 460), cv.FONT_HERSHEY_COMPLEX, 0.6, (0,0,255),2)
            #overlay indicator
            imgResult = cvzone.overlayPNG(imgResult, hudTopIndicator, [xAxisCam * 3, TOP_VERT + 350])#adds moving vertical
            imgResult = cvzone.overlayPNG(imgResult, hudSideIndicator, [SIDE_HORIZ + 350, yAxisCam * 2])
            #display video
            cv.namedWindow('TESTING HUD', cv.WINDOW_NORMAL)
            cv.imshow('TESTING HUD', imgResult)
            cv.resizeWindow('TESTING HUD', 1024, 600)
            #exit key
            if cv.waitKey(20) &0xFF == ord('q'):
                cv.destroyAllWindows()
                break

#serverProgram()
videoReciever.recieveRoverCam(ROVER_IP)