#!/usr/bin/env python
'''Press the button to turn on the pump.  Release to turn off.'''
import RPi.GPIO as GPIO
from PumpInterface import Pump


GPIO.setmode(GPIO.BCM)
pushbutton_pin = 25
GPIO.setup(pushbutton_pin, GPIO.IN)

pump = Pump()

previous_input = 0
while True:
    GPIO.setup(pushbutton_pin, GPIO.IN)
    pin_input = GPIO.input(pushbutton_pin)
    if ((previous_input == 0) and (pin_input == 1)):
        pump.start()
        previous_input = 1

    if ((previous_input == 1) and (pin_input == 0)):
        pump.stop()
        previous_input = 0


