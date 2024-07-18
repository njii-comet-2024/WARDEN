import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

while True:
	GPIO.output(13, GPIO.HIGH)
	GPIO.output(19, GPIO.HIGH)
