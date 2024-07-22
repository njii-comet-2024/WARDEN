from time import sleep
import RPi.GPIO as gpio

direction_pin   = 20
pulse_pin       = 21
cw_direction    = 0 
ccw_direction   = 1 

gpio.setmode(gpio.BCM)
gpio.setup(direction_pin, gpio.OUT)
gpio.setup(pulse_pin, gpio.OUT)
gpio.output(direction_pin,cw_direction)

try:
    while True:
        print('Direction CW')
        sleep(.5)
        gpio.output(direction_pin,cw_direction)
        for x in range(200):
            gpio.output(pulse_pin,gpio.HIGH)
            sleep(.001)
            gpio.output(pulse_pin,gpio.LOW)
            sleep(.0005)

        print('Direction CCW')
        sleep(.5)
        gpio.output(direction_pin,ccw_direction)
        for x in range(200):
            gpio.output(pulse_pin,gpio.HIGH)
            sleep(.001)
            gpio.output(pulse_pin,gpio.LOW)
            sleep(.0005)

except KeyboardInterrupt:
    gpio.cleanup()