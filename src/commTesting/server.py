"""
Server testing for video transmission

@author [Christopher Prol] [@prolvalone]

Date last modified: 07/16/2024
"""
# This is server code to send video frames over UDP
import cv2 as cv
import socket
import base64

CONNECTED = 0

class Camera: 
    def __init__(self):
        print("initializing")

    """
    Transmits Rover Video Data from a usb camera Over UDP sockets, acting as the server
    """
    def transmitUSBCamFeed():
        valX = 1
        valY = 1
        valHeight = 1
        valZoom = 1
        yAxisCam = 90
        xAxisCam = 105
        camHeight = 90
        zoom = 4

        bufferSize = 65536
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        hostName = socket.gethostname()
        hostIp = socket.gethostbyname(hostName)
        print(hostIp)
        port = 9999
        socketAddress = (hostIp, port)
        serverSocket.bind(socketAddress)
        print('Listening at:', socketAddress)

        vid = cv.VideoCapture(0)
        
        while True:
            
            msg, clientAddr = serverSocket.recvfrom(bufferSize)
            print('GOT connection from ', clientAddr)
            WIDTH = 1080
            HEIGHT = 400
            while vid.isOpened():
                #THIS IS TEST CODE BLOCK , DELETE LATER

                yAxisCam += valY
                xAxisCam += valX
                camHeight += valHeight
                zoom += valZoom

                if(yAxisCam >= 180 or yAxisCam <= 0):
                    valY *= -1
                if(xAxisCam >= 210 or xAxisCam <= 0):
                    valX *= -1
                if(camHeight >=180 or camHeight <=0):
                    valHeight *= -1
                if(zoom >=10 or zoom <=0):
                    valZoom *= -1
                print(camHeight, yAxisCam, xAxisCam, zoom)

                #DEELTE ABOVE

                cameraPos = bytearray([camHeight, yAxisCam, xAxisCam, zoom]) # height, tilt, rotation, zoom
                _, frame = vid.read()
                frame = cv.resize(frame, (WIDTH, HEIGHT))
                encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 50])

                message = base64.b64encode(buffer)
                combined = cameraPos + message
                serverSocket.sendto(combined, clientAddr)
            
                cv.imshow('TESTING HUD', frame)
                
                key = cv.waitKey(1) & 0xFF
                if key == ord('q'):
                    serverSocket.close()
                    cv.destroyAllWindows()
                    break

while True:
    Camera.transmitUSBCamFeed()







