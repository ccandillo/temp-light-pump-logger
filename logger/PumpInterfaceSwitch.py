#!/usr/bin/env python
'''Allows the pump to be controled by the onboard pushbutton switch'''
import sys
import time
import RPi.GPIO as GPIO
from PumpInterface import Pump

# configure logging
import logging
import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger('PumpInterfaceSwitch')

# configure gpio pins
pushbutton_pin = 25

# configure gpio
GPIO.setmode(GPIO.BCM)
GPIO.setup(pushbutton_pin, GPIO.IN)


class PumpSwitch(Pump):

    def __init__(self):
        Pump.__init__(self)

    def start(self):
        logger.info('POWER ON')
        GPIO.setup(self.pump_pin, GPIO.OUT)
        GPIO.output(self.pump_pin, True)

    def stop(self):
        logger.info('POWER OFF')
        GPIO.setup(self.pump_pin, GPIO.OUT)
        GPIO.output(self.pump_pin, False)
        GPIO.cleanup()


def run():
    '''Press the button to turn on the pump.  Release to turn off.'''

    pump = PumpSwitch()

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


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)