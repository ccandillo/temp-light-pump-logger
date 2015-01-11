#!/usr/bin/env python
import rrdtool
from os.path import join

# configure logging
import logging
import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger('DataInterface')


class Database:

    def __init__(self):
        pass

    def initialize_rrd(self):
        ''' Creates a Round Robin database to store ambient temperature,
            and light sensor readings.

            1 day   - 5 minuite resolution
            1 week  - 15 minuite resolution
            1 month - 1 hour resolution
            1 year  - 6 hour resolution
        '''
        DB = ('temperature.rrd', 'light.rrd')

        for db in DB:
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

#if __name__ == '__main__':
    #db = Database()
    #db.initialize_rrd()