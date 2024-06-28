
# This is client code to receive video frames over UDP
import cv2, imutils, socket
import numpy as np
import time
import base64

<<<<<<< HEAD
bufferSize = 65536
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
hostName = socket.gethostname()
hostIp = '10.255.0.137'#  socket.gethostbyname(host_name)
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
=======
BUFF_SIZE = 65536
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '172.16.224.229' #socket.gethostbyname(host_name)
print(host_ip)
port = 9999
message = b'Hello'

client_socket.sendto(message, (host_ip,port))
fps, st, frames_to_count, cnt = (0, 0, 20, 0)
while True:
	packet,_ = client_socket.recvfrom(BUFF_SIZE)
	data = base64.b64decode(packet, ' /')
	npdata = np.fromstring(data, dtype=np.uint8)
	frame = cv2.imdecode(npdata, 1)
	frame = cv2.putText(frame, 'FPS: '+ str(fps), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
>>>>>>> a5d8ef8361a9446ca0abb14f3c97b5bec7cd17bb
	cv2.imshow("RECEIVING VIDEO", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		clientSocket.close()
		break
	if cnt == framesToCount:
		try:
<<<<<<< HEAD
			fps = round(framesToCount/(time.time()-st))
			st=time.time()
			cnt=0
=======
			fps = round(frames_to_count / (time.time() - st))
			st = time.time()
			cnt = 0
>>>>>>> a5d8ef8361a9446ca0abb14f3c97b5bec7cd17bb
		except:
			pass
	cnt += 1