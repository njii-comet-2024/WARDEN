'''
recieves camera feed from the rover and displays it

@author [Vito Tribuzio][Snoopy-0]

Date last modified: 07/22/2024
'''

#libraries
import cv2
import socket
import struct
import pickle
import numpy as np

#These are for WARDEN and should be same for EXT since they are static IPS
#RoverCam = 192.168.110.169
#Drone =  192.168.110.???
#Rover  = 192.168.110.19
#Central = 192.168.110.5

#socket parameters
hostIP = '192.168.110.78'
hostPort = 9999

#initialize socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((hostIP, hostPort))
serverSocket.listen(5)
print("Listening for connections...")

# Accept connection
clientSocket, addr = serverSocket.accept()
print(f"Connection from: {addr}")
connection = clientSocket.makefile('rb')

while True:
    # Read message length
    packed_msg_size = connection.read(struct.calcsize("Q"))
    if not packed_msg_size:
        break

    msg_size = struct.unpack("Q", packed_msg_size)[0]

    # Read message data
    data = b""
    while len(data) < msg_size:
        data += connection.read(msg_size - len(data))

    # Deserialize frame
    frame_data = pickle.loads(data)
    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Display frame
    cv2.imshow("Receiving Video", frame_rgb)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
connection.close()
clientSocket.close()
serverSocket.close()
cv2.destroyAllWindows()