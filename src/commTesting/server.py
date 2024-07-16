"""
Server testing for video transmission

@author [Christopher Prol] [@prolvalone]

Date last modified: 07/16/2024
"""
# This is server code to send video frames over UDP
import cv2 as cv
import socket
import base64

class Camera:
    def __init__(self):
        print("initializing")

    """
    Transmits Rover Video Data from a usb camera Over UDP sockets, acting as the server
    """
    def transmitUSBCamFeed():
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
        cameraPos = bytearray([10, 69, 90, 170])

        while True:
            # if arduino.in_waiting:
            #     arduino.readinto(cameraPos)  # bytearray

            msg, clientAddr = serverSocket.recvfrom(bufferSize)
            print('GOT connection from ', clientAddr)
            WIDTH = 400
            HEIGHT = 1080
            while vid.isOpened():
                _, frame = vid.read()
                frame = cv.resize(frame, (WIDTH, HEIGHT))
                encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

                message = base64.b64encode(buffer)
                combined = cameraPos + message
                serverSocket.sendto(combined, clientAddr)
                
                cv.imshow('TRANSMITTING VIDEO', frame)
                key = cv.waitKey(1) & 0xFF
                if key == ord('q'):
                    serverSocket.close()
                    break


Camera.transmitUSBCamFeed()