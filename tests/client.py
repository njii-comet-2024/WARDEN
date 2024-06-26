import struct
import cv2
import socket
import pickle

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostIp = '10.255.0.137'
port = 7777
clientSocket.connect((hostIp, port))
data = b""
payloadSize = struct.calcsize("Q")

while True:
    while len(data) < payloadSize:
        packet = clientSocket.recv(4 * 1024)
        if not packet: break
        data += packet

    packedMessageSize = data[:payloadSize]
    data = data[payloadSize:]
    messageSize = struct.unpack("Q", packedMessageSize)[0]

    while len(data) < messageSize:
        data += clientSocket.recv(4 * 1024)

    frameData = data[:messageSize]
    data = data[messageSize:]
    frame = pickle.loads(frameData)
    cv2.imshow("RECEIVING VIDEO", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

clientSocket.close()
