#This is a test code for the server


import struct, socket, pickle
import cv2

#create socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostName = socket.gethostname()
hostIp = socket.gethostbyname(hostName)
print('HOST IP:', hostIp)
port = 7777
socketAddress = (hostIp, port)

#bind socket
serverSocket.bind(socketAddress)

#listen
serverSocket.listen(5)
print ('Listening AT:', socketAddress)

#accept  
while True:
    clientSocket,addr = serverSocket.accept()
    print('GOT CONNECECTION FROM:', addr)
    if clientSocket:
        vid = cv2.VideoCapture(0)
        while(vid.isOpened()):
            img,frame = vid.read()
            a = pickle.dumps(frame)
            message=struct.pack("Q",len(a))+a
            clientSocket.sendall(message)
            cv2.imshow('TRANSMITTING VIDEO', frame)
            key = cv2.waitKey(1) & 0xFF
            if key ==ord('q'):
                clientSocket.close()

