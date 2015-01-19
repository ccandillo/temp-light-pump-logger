#!/usr/bin/env python
import ConfigParser
from glob import glob
from os import remove
from os.path import join, splitext, basename
from flask import Flask, flash, render_template, redirect, url_for, request
import rrdtool
import GraphInterface
from apscheduler.scheduler import Scheduler
from DataInterface import Database
from TemperatureInterface import Temperature
from LightInterface import Light
from PumpInterfaceSwitch import PumpSwitch

# configure logging
import logging
import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger('app')
sched = Scheduler()

# configure database connection
db = Database()

# configure pump interface
pump = PumpSwitch()


def sensor_job():
    print('Updating sensors')
    temp_sensor = Temperature().read_temp()
    light_sensor = Light().RCtime()
    db.update(temp_sensor, light_sensor)


def graph_job():
    print('Updating graphs')
    GraphInterface.create(period='daily')
    GraphInterface.create(period='weekly')
    GraphInterface.create(period='monthly')
    GraphInterface.create(period='yearly')

sched.add_interval_job(sensor_job, minutes=1)
sched.add_interval_job(graph_job, minutes=1, seconds=30)
sched.start()
#sched.print_jobs()


app = Flask(__name__)
app.secret_key = 'some secret'


@app.route('/', methods=['GET', 'POST'])
def daily_graphs():
    if request.method == 'POST':
        if request.form.get('On', None) == 'on':
            pump.start()
            #flash('The pump is running.')
        if request.form.get('Off', None) == 'off':
            pump.stop()
            #flash('The pump has stopped.')

    return render_template('index.html')

@app.route('/logs')
def logs():
    log_handler = logger.__dict__['handlers'][0]
    log_filename = log_handler.baseFilename
    if log_filename:
        return open(log_filename).readline()
    return 'No file found'


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
