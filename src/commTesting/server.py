
# This is server code to send video frames over UDP
import cv2, imutils, socket
import numpy as np
import time
import base64

bufferSize = 65536
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufferSize)
hostName = socket.gethostname()
hostIp = '10.255.0.137'#  socket.gethostbyname(hostName)
print(hostIp)
port = 9999
socketAddress = (hostIp,port)
serverSocket.bind(socketAddress)
print('Listening at:', socketAddress)

vid = cv2.VideoCapture(0) #  replace 'rocket.mp4' with 0 for webcam
fps, st, framesToCount, cnt = (0,0,20,0)

while True:
	msg,clientAddr = serverSocket.recvfrom(bufferSize)
	print('GOT connection from ', clientAddr)
	WIDTH=400
	while(vid.isOpened()):
		_,frame = vid.read()
		frame = imutils.resize(frame,width=WIDTH)
		encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY,80])
		message = base64.b64encode(buffer)
		serverSocket.sendto(message,clientAddr)
		frame = cv2.putText(frame, 'FPS: '+str(fps), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
		cv2.imshow('TRANSMITTING VIDEO', frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord('q'):
			serverSocket.close()
			break
		if cnt == framesToCount:
			try:
				fps = round(framesToCount/(time.time()-st))
				st=time.time()
				cnt=0
			except:
				pass
		cnt+=1

