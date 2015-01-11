#!/usr/bin/env python
import sys
import time
import argparse
import rrdtool
from os.path import join
from DataInterface import Database
from TemperatureInterface import Temperature
from LightInterface import Light

# configure logging
import logging
import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger('LoggerController')


parser = argparse.ArgumentParser()
parser.add_argument('--initdb', action='store_true',
                    help='Create a new database')
parser.add_argument('--debug', action='store_true',
                    help='Loops forever and writes output to stdout')
parser.add_argument('--verbose', action='store_true',
                    help='Runs once and writes output to stdout')
args = parser.parse_args()

db = Database()
if args.initdb:
    db.initialize()


def main():
    ''' Creates Global RRD's for temperture and light sensors if passed the
        --initdb commandline argument.

        Queries the temperature and light sensor values.

        Updates the RRD's with the current values.

        If in 'verbose' mode it prints status output to screen and
        then quits after one query.

        If in DEBUG mode it prints staus output to the screen and loops
        'main()' forever.'''

    while True:
        temp_sensor = Temperature().read_temp()
        if args.debug or args.verbose:
            logger.debug(('Polled current temperature as {0} celsius'.format(
                                                                temp_sensor)))
        light_sensor = Light().RCtime()
        if args.debug or args.verbose:
            logger.debug(('Polled current lighting as {0} lux'.format(
                                                                light_sensor)))

        db.update(temp_sensor, light_sensor)
        time.sleep(1)
        if not args.debug:
            break
        if args.verbose:
            break


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
