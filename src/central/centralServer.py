"""
sets up server for all vehicles to connect too - - - acts as client
@author [Vito Tribuzio]     [@Snoopy-0]
        [Christopher Prol]  [@prolvalone]

Date last modified: 07/15/2024
"""

# Libraries
import socket
import cv2 as cv
import numpy as np 
import base64
import cvzone



#initial capture
#capture  = cv.VideoCapture(0)
#ret, frame = capture.read()


ROVER_IP = '192.168.110.253'
TOP_HORIZ = -293
TOP_VERT = -340
SIDE_VERT = -370
SIDE_HORIZ = -340

"""
This is some sort of test 
"""
def serverProgram():
    #create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #reserved a port on computer, can be anything
    port = 12345

    #bind to the port, no ip in ip field which makes server listen to request
    s.bind(('', port))
    print ("socket binded to %s" %(port))

    #put socket into listening mode
    s.listen(5)
    print ("socket is listening")

    #accept new connection
    c, addr = s.accept()
    print ('Got connection from', addr)

    data = input(' -> ')

    while True:
        #recieve data from client and print it
        #data = c.recv(1024).decode()
        #print("from connected user: " + str(data))

        #send data to the client
        c.send(data.encode())

        #if statement to break the cycle
        if data == 'endServer':
            break

        data = input(' -> ')

    #Close the connection
    c.close()
"""
This is a class for video reception
"""
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
                cv.destroyWindow('TESTING HUD')

#serverProgram()
videoReciever.recieveRoverCam(ROVER_IP)