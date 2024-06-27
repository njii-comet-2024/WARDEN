import struct
import cv2
import socket
import pickle

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
hostIp = '172.16.224.229'  # Change to server's IP
port = 7777
serverAddress = (hostIp, port)

# Send initial message to server to initiate communication
clientSocket.sendto(b'Hello', serverAddress)

data = b""
payloadSize = struct.calcsize("Q")

while True:
    while len(data) < payloadSize:
        packet, _ = clientSocket.recvfrom(4 * 1024)
        if not packet:
            break
        data += packet

    packedMessageSize = data[:payloadSize]
    data = data[payloadSize:]
    messageSize = struct.unpack("Q", packedMessageSize)[0]

    while len(data) < messageSize:
        packet, _ = clientSocket.recvfrom(4 * 1024)
        if not packet:
            break
        data += packet

    frameData = data[:messageSize]
    data = data[messageSize:]
    frame = pickle.loads(frameData)
    cv2.imshow("RECEIVING VIDEO", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

clientSocket.close()
