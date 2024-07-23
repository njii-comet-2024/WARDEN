"""
Sets up server for connection with pi on the drone. received video feed from external camera

@author [Vito Tribuzio][@Snoopy-0]
        [Zoe Rizzo][zizz-0]

Date last modified: 07/23/2024
"""
import cv2 as cv
import socket
import struct
import pickle
import numpy as np

# Socket parameters
hostIp = '192.169.110.5'
hostPort = 5000

# Initialize socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((hostIp, hostPort))
serverSocket.listen(5)
print("Listening for connections...")

# Accept connection
clientSocket, addr = serverSocket.accept()
print(f"Connection from: {addr}")
connection = clientSocket.makefile('rb')

while True:
    # Read message length
    packedMsgSize = connection.read(struct.calcsize("Q"))
    if not packedMsgSize:
        break

    msgSize = struct.unpack("Q", packedMsgSize)[0]

    # Read message data
    data = b""
    while len(data) < msgSize:
        data += connection.read(msgSize - len(data))

    # Deserialize frame
    frameData = pickle.loads(data)
    frame = cv.imdecode(np.frombuffer(frameData, dtype=np.uint8), cv.IMREAD_COLOR)

    frameRgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    # Display frame
    cv.imshow("Receiving Video", frameRgb)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
connection.close()
clientSocket.close()
serverSocket.close()
cv.destroyAllWindows()
