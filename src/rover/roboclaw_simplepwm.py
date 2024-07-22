import time
from roboclaw import Roboclaw

#Windows comport name
# rc = Roboclaw("COM11",115200)
#Linux comport name
rc = Roboclaw("/dev/serial0", 2800)

rc.Open()
address = 0x80

while True:
	rc.ForwardM1(address,32)	#1/4 power forward
	print("fwd m1")
	rc.BackwardM2(address,32)	#1/4 power backward
	print("back m2")
	time.sleep(2)
	print("sleep")
	
	rc.BackwardM1(address,32)	#1/4 power backward
	print("back m1")
	rc.ForwardM2(address,32)	#1/4 power forward
	print("fwd m2")
	time.sleep(2)
	print("sleep")

	rc.BackwardM1(address,0)	#Stopped
	print("m1 stop")
	rc.ForwardM2(address,0)		#Stopped
	print("m2 stop")
	time.sleep(2)
	print("sleep")

	m1duty = 16
	m2duty = -16
	rc.ForwardBackwardM1(address,64+m1duty)	#1/4 power forward
	print("fwd m1")
	rc.ForwardBackwardM2(address,64+m2duty)	#1/4 power backward
	print("back m2")
	time.sleep(2)
	print("sleep")
	
	m1duty = -16
	m2duty = 16
	rc.ForwardBackwardM1(address,64+m1duty)	#1/4 power backward
	print("back m1")
	rc.ForwardBackwardM2(address,64+m2duty)	#1/4 power forward
	print("fwd m2")
	time.sleep(2)
	print("sleep")

	rc.ForwardBackwardM1(address,64)	#Stopped
	print("m1 stop")
	rc.ForwardBackwardM2(address,64)	#Stopped
	print("m2 stop")
	time.sleep(2)
	print("sleep")
	
