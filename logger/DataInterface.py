#!/usr/bin/env python
import rrdtool
from os.path import join, splitext

# configure logging
import logging
import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger('DataInterface')


class Database:

    def __init__(self):
        self.databases = ('temperature.rrd', 'light.rrd')

    def initialize(self):
        ''' Creates a Round Robin database to store ambient temperature,
            and light sensor readings.

            1 day   - 5 minuite resolution
            1 week  - 15 minuite resolution
            1 month - 1 hour resolution
            1 year  - 6 hour resolution
        '''

        for db in self.databases:
            logger.info('Initializing a blank {0}'.format(db))
            ret = rrdtool.create(join('rrd', db),
                                 '--step', '300', '--start', '0',
                                 'DS:input:GAUGE:600:U:U',
                                 'RRA:MIN:0.5:1:288',
                                 'RRA:MIN:0.5:3:672',
                                 'RRA:MIN:0.5:12:744',
                                 'RRA:MIN:0.5:72:1480',
                                 'RRA:AVERAGE:0.5:1:288',
                                 'RRA:AVERAGE:0.5:3:672',
                                 'RRA:AVERAGE:0.5:12:744',
                                 'RRA:AVERAGE:0.5:72:1480',
                                 'RRA:MAX:0.5:1:288',
                                 'RRA:MAX:0.5:3:672',
                                 'RRA:MAX:0.5:12:744',
                                 'RRA:MAX:0.5:72:1480',)

            if ret:
                logger.debug(rrdtool.error())
            logger.info('{0} created'.format(db))

    def update(self, temperature_sensor, light_sensor):
        ''' Update the round robin databases with the new sensor readings '''

        #Updates global temperature and light RRD's
        for db in self.databases:
            sensor = splitext(db)[0] + '_sensor'
            try:
                rrdtool.update(join('rrd', db), 'N:' + str(sensor))
            except rrdtool.error:
                logger.debug((rrdtool.error()))


if __name__ == '__main__':
    db = Database()
    db.initialize()