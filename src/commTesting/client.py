"""
Client Side Video testing

@author  [Christopher Prol] [@prolvalone]

Date last modified: 07/08/2024
"""
# This is client code to receive video frames over UDP
import cv2, imutils, socket 
import numpy as np 
import time
import base64

bufferSize = 65536
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
hostName = socket.gethostname()
hostIp = '10.255.0.255'#  socket.gethostbyname(hostName)
print(hostIp)
port = 9999
message = b'Hello'

clientSocket.sendto(message, (hostIp,port))
fps, st, framesToCount, cnt = (0,0,20,0)
while True:
	packet,_ = clientSocket.recvfrom(bufferSize)
	data = base64.b64decode(packet, ' /')
	npdata = np.fromstring(data, dtype=np.uint8)
	frame = cv2.imdecode(npdata, 1)
	frame = cv2.putText(frame, 'FPS: '+str(fps), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	cv2.imshow("RECEIVING VIDEO", frame)
	key = cv2.waitKey(1) & 0xFF
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



