from gpiozero import Motor
from time import sleep

motor = Motor(forward=13, backward=19)

while True:
    motor.forward()
    sleep(5)
    motor.backward()
    sleep(5)