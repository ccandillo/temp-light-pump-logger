#!/usr/bin/env python
''' Take light readings using a photo cell resistor

Code taken from Adafruit:
http://learn.adafruit.com/basic-resistor-sensor-reading-on-raspberry-pi

'''
import RPi.GPIO as GPIO
import time


class Light:

    def __init__(self):
        ''' Setup gpio pins and mode. '''

        self.photoresister_pin = 18
        GPIO.setmode(GPIO.BCM)

    def RCtime(self):
        ''' Read light sensor '''

        reading = 0
        GPIO.setup(self.photoresister_pin, GPIO.OUT)
        GPIO.output(self.photoresister_pin, GPIO.LOW)
        time.sleep(0.1)

        GPIO.setup(self.photoresister_pin, GPIO.IN)

        # This take about 1 milisecond per loop cycle
        while (GPIO.input(self.photoresister_pin) == GPIO.LOW):
            reading += 1
        return reading


if __name__ == '__main__':
    light = Light()
    print((light.RCtime()))
