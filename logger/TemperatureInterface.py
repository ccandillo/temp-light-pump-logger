#!/usr/bin/env python
''' Take temperature readings using the DS18B20 chip

Code taken from Adafruit:
http://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing
'''
import os
import glob
import time

# temperature interface
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


class Temperature:

    def __init__(self):
        ''' Finds the file that the sensor writes to. '''

        self.base_dir = '/sys/bus/w1/devices/'
        self.device_folder = glob.glob(self.base_dir + '28*')[0]
        self.device_file = self.device_folder + '/w1_slave'  # lint:ok

    def _read_temp_raw(self):
        ''' Reads the temperature from the file '''

        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        ''' Checks for bad messages and returns the temperature in celsius. '''

        lines = self._read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self._read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c


if __name__ == '__main__':
    temp = Temperature()
    print((temp.read_temp()))
