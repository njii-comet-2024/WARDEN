"""
sets up server for all vehicles to connect too
@author [Vito Tribuzio] [@Snoopy-0]
        [Christopher Prol] [@prolvalone]

Date last modified: 07/9/2024
"""

# Libraries
import socket
import sys
import cv2 as cv
import imutils
import numpy as np 
import time
import base64



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
        bufferSize = 65536
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
        hostName = socket.gethostname()
        #roverIP = '192.168.110.255'     - - - -   could delete function Param for this instead
        print(roverIP)
        port = 9999                                 # can change based on possible interference, etc
        message = b'Hello'                          # test message

        clientSocket.sendto(message, (roverIP,port))
        fps, st, framesToCount, cnt = (0,0,20,0)
        while True:
            packet,_ = clientSocket.recvfrom(bufferSize)
            data = base64.b64decode(packet, ' /')
            npdata = np.fromstring(data, dtype=np.uint8)
            frame = cv.imdecode(npdata, 1)
            frame = cv.putText(frame, 'FPS: '+str(fps), (10,40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2) # shows FPS, can likely be deleted
            cv.imshow("RECEIVING VIDEO", frame)    # display Video

        #Exit Key
            key = cv.waitKey(1) & 0xFF
            if key == ord('q'):
                clientSocket.close()
                break
            if cnt == framesToCount:
                try:
                    fps = round(framesToCount/(time.time()-st))
                    st=time.time()
                    cnt=0
                except:
                    pass
            cnt+=1


serverProgram()