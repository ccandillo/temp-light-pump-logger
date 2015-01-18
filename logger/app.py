#!/usr/bin/env python
import ConfigParser
from glob import glob
from os import remove
from os.path import join, splitext, basename
from flask import Flask, flash, render_template, redirect, url_for, request
import rrdtool
#import alert
import GraphInterface
from apscheduler.scheduler import Scheduler
from DataInterface import Database
from TemperatureInterface import Temperature
from LightInterface import Light

# configure logging
import logging
import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger('app')
sched = Scheduler()

# get webdir path
config = ConfigParser.ConfigParser()
config.read('config.ini')
webdir = config.get('graph', 'webdir')

# configure database connection
db = Database()


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

def get_probe_number(probe):
    ''' Returns the probed number '''

    return (basename(probe)).split('-')[-1].split('_')[0]

def get_moisture_sensor_graphs(path, period='daily'):
    ''' Returns moisture sensor graphs '''

    fname = 'moisture' + '*_' + period + '.png'
    images = sorted(glob(join(webdir, fname)))
    probe_numbers = [get_probe_number(probe)
                     for probe in images]

    return zip(probe_numbers, images)

def get_config_ini():
    ''' Returns current config.ini settings '''

    results = {}
    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    for section in config.sections():
        results[section] = config.items(section)

    return results

def set_config_ini(data):
    ''' I create a dictionary of the contents of config.ini and
        update conig.ini with any new settings '''

    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    sections = {}
    for section in config.sections():
        sections[section] = config.items(section)

    for label, text in data:
        for section in sections.keys():
            for option, value in sections[section]:
                if label == option:
##                    print 'label: %s \t option: %s' % (text, value)
                    config.set(section, option, value=str(text))

    with open('config.ini', 'wb') as configfile:
        config.write(configfile)

def get_moisture_probes():
    ''' Returns the list of moisture probe databases '''

    probes = glob(join('rrd', 'moisture*'))
    return probes

def delete_moisture_probes(fnames):
    images = []
    for fname in fnames:
        name = splitext(basename(fname))[0]
        images.extend(glob(join(webdir, name + '*')))

    fnames.extend(images)
    print fnames
    [ remove(fname) for fname in fnames ]

@app.route('/')
def daily_graphs():
    return render_template('index.html')

#@app.route('/')
#def daily_graphs():
    #ret = alert.main()
    #if ret:
        #for probe_name, probe_number, last_update in ret:
            #message = probe_name.capitalize() + ' Probe ' + str(probe_number) + ' needs water!'
            #flash(message)
    #return render_template('index.html',
                           #probes=get_moisture_sensor_graphs(webdir,
                                                             #period='daily'))

#@app.route('/weekly')
#def weekly_graphs():
    #return render_template('weekly.html',
                           #probes=get_moisture_sensor_graphs(webdir,
                                                             #period='weekly'))

#@app.route('/monthly')
#def monthly_graphs():
    #return render_template('monthly.html',
                           #probes=get_moisture_sensor_graphs(webdir,
                                                             #period='monthly'))

#@app.route('/yearly')
#def yearly_graphs():
    #return render_template('yearly.html',
                           #probes=get_moisture_sensor_graphs(webdir,
                                                             #period='yearly'))

#@app.route('/config')
#def config_page():
    #return render_template('config.html',
                           #sections=get_config_ini(),
                           #probes=get_moisture_probes())

#@app.route('/update_config', methods=['GET', 'POST'])
#def update_config():
    #flash('Saved settings.')
    #f = request.form
    #set_config_ini(f.items())
    #return redirect(url_for('config_page'))

#@app.route('/delete_probes', methods=['GET', 'POST'])
#def delete_probes():
    #f = request.form.getlist('probe')
    #delete_moisture_probes(f)
    #return redirect(url_for('config_page'))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
