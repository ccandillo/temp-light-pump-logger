#!/usr/bin/env python
'''Press the button to turn on the pump.  Release to turn off.'''
import time
import RPi.GPIO as GPIO
from PumpInterface import Pump

# configure logging
import logging
import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger('PumpInterfaceSwitch')


class PumpSwitch(Pump):

    def __init__(self):
        Pump.__init__(self)

    def start(self):
        logger.info('POWER ON')
        GPIO.setup(self.pump_pin, GPIO.OUT)
        GPIO.output(self.pump_pin, True)

    def stop(self):
        logger.info('POWER OFF')
        GPIO.output(self.pump_pin, False)
        GPIO.cleanup()

    def run(self, duration=2):
        logger.info(('Running pump for {0} seconds'.format(duration)))
        self.start()
        time.sleep(duration)
        self.stop()


GPIO.setmode(GPIO.BCM)
pushbutton_pin = 25
GPIO.setup(pushbutton_pin, GPIO.IN)

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


