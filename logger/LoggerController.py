#!/usr/bin/env python
''' Read SPI data from the MCP3008 chip, 8 possible adc's (0 thru 7)

    Pin 0 is the moisture seonsor 1 on the ADC
    Pin 18 is the light sensor on the GPIO
    Pin 4 is the temperature sensor on the GPIO
'''
import sys
import spidev
import time
import argparse
import rrdtool
import ConfigParser
import RPi.GPIO as GPIO
import read_temperature as rt
from os import chown
from os.path import join, exists
from pwd import getpwnam
from datetime import datetime
from read_light import RCtime
from make_rrd import make_rrd
import graph

config = ConfigParser.ConfigParser()
config.read('config.ini')

DEBUG = config.getboolean('main', 'debug')
SAMPLE_RATE = config.getint('main', 'sample_rate') #polls sensors every second, add ~2 second skew 
TOTAL_PROBES = config.getint('main', 'total_probes')
PHOTOCELL_PIN = 18

#GPIO setup
GPIO.setmode(GPIO.BCM)

#SPI analog to digital converter setup
spi = spidev.SpiDev()
spi.open(0, 0)

parser = argparse.ArgumentParser()
parser.add_argument('--initdb', action='store_true',
                    help='Create a new database')
parser.add_argument('--debug', action='store_true',
                    help='Do run run in debug mode')
parser.add_argument('--verbose', action='store_true',
                    help='Verbose')
args = parser.parse_args()
verbose=args.verbose

if args.initdb:
    import init_rrd

if args.debug:
    DEBUG = True

def read_adc(adcnum):
    ''' Read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7) '''
    
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    adcout = ((r[1] & 3) << 8) + r[2]
    return adcout

def get_light(pin=PHOTOCELL_PIN):
    ''' Read photocell sensor '''
    
    return RCtime(pin)

def get_temp():
    ''' Read tempeature sensor '''

    return rt.read_temp()

def create_global_rrd(sensors=['temperature.rrd', 'light.rrd']):
    ''' Creates temperature and light rrd if none exists. '''

    for sensor in sensors:
        if not exists(join('rrd', sensor)):
            make_rrd(sensor)


def create_probe_rrd():
    ''' Checks to see if an rrd exists, if not it creates one '''

    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    TOTAL_PROBES = config.getint('main', 'total_probes')

    for probe in range(TOTAL_PROBES):
        fname = 'moisture' + '-' + str(probe) + '.rrd'
        if not exists(join('rrd', fname)):
            make_rrd(fname)
            chown(join('rrd', fname),
                  getpwnam('pi').pw_uid,
                  getpwnam('pi').pw_gid)

def update_rrd(temp_sensor, light_sensor, moisture_sensors):
    ''' Update the round robin databases with the new sensor readings '''

    DB = {'temperature.rrd': temp_sensor,
          'light.rrd': light_sensor}

    #Updates global temperature and light RRD's
    for db in DB.keys():
        ret = rrdtool.update(join('rrd', db), 'N:' + str(DB[db]))
        if ret:
            print rrdtool.error()

    #Updates moisture sensor RRD's
    for sensor in range(len(moisture_sensors)):
        fname = 'moisture' + '-' + str(sensor) + '.rrd'
        ret = rrdtool.update(join('rrd', fname),
                             'N:' + str(moisture_sensors[sensor]))
        if ret:
            print rrdtool.error()
    
def main(verbose=verbose):
    ''' Read the adc then quits. If in DEBUG mode it polls continuously
        using the SAMPLE_RATE.

        Creates Global RRD's for temperture and light sensors. Queries
        the temperature and light sensor values.

        Currently supports up to 8 moisture probes on a single MD3008
        chip (channels 0-7).  Those probes are queried and stored in the
        'moisture_sensors' list.

        Updates the RRD's with the current values.

        If in 'verbose' mode it prints status output to screen and
        then quits after one query.
        
        If in DEBUG mode it prints staus output to the screen and loops
        'main()' forever.'''

    create_global_rrd()
    
    while True:
        moisture_sensors = []
        
        time_now = datetime.now().ctime()
        temp_sensor = get_temp()
        light_sensor = get_light()

        for probe in range(TOTAL_PROBES):
            moisture_sensors.append(read_adc(probe))
        
        if DEBUG or verbose:
            print "[%s]  Temp: %s C\t Light: %s" % (time_now,
                                                    temp_sensor,
                                                    light_sensor)
            for i in range(len(moisture_sensors)):
                print " Probe %s: %s" % (i, moisture_sensors[i])

        create_probe_rrd()
        update_rrd(temp_sensor, light_sensor, moisture_sensors)
        time.sleep(SAMPLE_RATE)
        if not DEBUG:
            break
        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit(0)
        

