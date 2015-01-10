#!/usr/bin/env python
''' Turns on the submersible pump using a powertail switch.'''
import sys
import time
import RPi.GPIO as GPIO


class Pump:

    def __init__(self):
        # setup raspberry pi pin numbers
        self.pump_pin = 23

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pump_pin, GPIO.OUT)
        GPIO.output(self.pump_pin, False)

    def start(self):
        print('POWER ON')
        GPIO.setup(self.pump_pin, GPIO.OUT)
        GPIO.output(self.pump_pin, True)

    def stop(self):
        print('POWER OFF')
        GPIO.output(self.pump_pin, False)
        GPIO.cleanup()

    def run(self, duration=2):
        print(('Running pump for {0} seconds'.format(duration)))
        self.start()
        time.sleep(duration)
        self.stop()


if __name__ == '__main__':
    pump = Pump()
    pump.run()
