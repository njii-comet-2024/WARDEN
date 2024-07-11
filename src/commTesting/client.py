"""
Client Side Video testing

@author  [Christopher Prol] [@prolvalone]

Date last modified: 07/11/2024
"""
# This is client code to receive video frames over UDP
import cv2, imutils, socket
import numpy as np
import time
import base64
import struct

bufferSize = 65536
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
hostName = socket.gethostname()
hostIp = '172.168.10.137' # socket.gethostbyname(hostName)
print(hostIp)
port = 9999
message = b'Hello'

clientSocket.sendto(message, (hostIp, port))
fps, st, framesToCount, cnt = (0, 0, 20, 0)
while True:
    packet, _ = clientSocket.recvfrom(bufferSize)
    # Extract the integer value (4 bytes) and the rest as base64 encoded data
    int_value = struct.unpack('!I', packet[:4])[0]
    data = base64.b64decode(packet[4:], ' /')
    npdata = np.fromstring(data, dtype=np.uint8)
    frame = cv2.imdecode(npdata, 1)
    frame = cv2.putText(frame, 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    frame = cv2.putText(frame, 'Value: ' + str(int_value), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("RECEIVING VIDEO", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        clientSocket.close()
        break
    if cnt == framesToCount:
        try:
            fps = round(framesToCount / (time.time() - st))
            st = time.time()
            cnt = 0
        except:
            pass
    cnt += 1

cv2.destroyAllWindows()
