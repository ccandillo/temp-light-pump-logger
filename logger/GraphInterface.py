#!/usr/bin/env python
''' Creates the graphs from the rrd sensor data.'''
import rrdtool
import ConfigParser
from pwd import getpwnam
from os import chown
from os.path import join, basename
from glob import glob

# configure logging
import logging
import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger('GraphInterface')


config = ConfigParser.ConfigParser()
config.read('config.ini')

webdir = config.get('graph', 'webdir')
color = config.get('graph', 'color')

temperature = {'image': join(webdir, 'temperature.png'),
               'label': 'Celsius',
               'title': 'Temperature',
               'db': join('rrd', 'temperature.rrd'),
               'legend': 'Temp',
               'unit': 'C',
               'upper_limit': ''}

light = {'image': join(webdir, 'light.png'),
         'label': 'Bright <-  -> Dark',
         'title': 'Light',
         'db': join('rrd', 'light.rrd'),
         'legend': 'Light',
         'unit': '',
         'upper_limit': ''}

periods = {'daily': '1d',
           'weekly': '1w',
           'monthly': '1m',
           'yearly': '1y'}


def get_xgrid(period):
    ''' Adjust --x-grid based on daily, weekly, monthly
        or yearly graphs'''

    if period == 'daily':
        return 'HOUR:1:HOUR:1:HOUR:2:0:%H'
    if period == 'weekly':
        return 'HOUR:6:DAY:1:DAY:1:86400:%a'
    if period == 'monthly':
        return 'DAY:1:WEEK:1:WEEK:1:86400:%d %b'
    if period == 'yearly':
        return 'WEEK:1:WEEK:4:WEEK:4:86400:%b'


def create(period='daily'):
    ''' Reads all files in the /rrd root directory. For each file
        only the 'img_name' and 'db' (rrd file) change to refect the
        current file.  Using the template dictionary's above for
        temperature, light and mosture, an rrd graph is created and
        saved in 'webdir'.
    '''

    xgrid = get_xgrid(period)

    for db in (glob('rrd/*.rrd')):
        logger.info('Updating {0} {1} graph'.format(db, period))
        db_name = basename(db)
        img_name = db_name.split('.')[0] + '_' + period + '.png'
        dict_name = db_name.split('.')[0].split('-')[0]

        sensor = eval(dict_name)

        sensor['image'] = join(webdir, img_name)
        sensor['db'] = db
        original_title = sensor['title']
        sensor['title'] = period.capitalize() + ' ' + sensor['title']

        ret = rrdtool.graph(sensor['image'], '--start', '-' + periods[period],
                            '--vertical-label=' + sensor['label'],
                            '--title=' + sensor['title'],
                            '--x-grid', xgrid,
                            'DEF:input=' + sensor['db'] + ':input:AVERAGE',
##                            'AREA:input#0EA26B:' + sensor['legend'],
                            'AREA:input' + color + ':' + sensor['legend'],
                            'GPRINT:input:LAST:Current\: %6.2lf%S' + sensor['unit'],
                            'GPRINT:input:AVERAGE:Ave\: %6.2lf%S' + sensor['unit'],
                            'GPRINT:input:MAX:Max\: %6.2lf%S' + sensor['unit'])

        sensor['title'] = original_title
        chown(sensor['image'],
              getpwnam('pi').pw_uid,
              getpwnam('pi').pw_gid)


if __name__ == '__main__':

    create(period='daily')
    create(period='weekly')
    create(period='monthly')
    create(period='yearly')
