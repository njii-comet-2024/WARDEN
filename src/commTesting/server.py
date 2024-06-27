import struct, socket, pickle
import cv2

# Create UDP socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
hostName = socket.gethostname()
hostIp = socket.gethostbyname(hostName)
print('HOST IP:', hostIp)
port = 7777
socketAddress = (hostIp, port)

# Bind socket
serverSocket.bind(socketAddress)
print('Listening AT:', socketAddress)

while True:
    msg, clientAddr = serverSocket.recvfrom(1024)  # Expecting a small message to get client address
    print('GOT CONNECTION FROM:', clientAddr)
    vid = cv2.VideoCapture(0)
    while vid.isOpened():
        ret, frame = vid.read()
        if not ret:
            break
        a = pickle.dumps(frame)
        message = struct.pack("Q", len(a)) + a
        serverSocket.sendto(message, clientAddr)
        cv2.imshow('TRANSMITTING VIDEO', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    vid.release()
    cv2.destroyAllWindows()
