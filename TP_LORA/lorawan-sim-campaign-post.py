#!/usr/bin/env python3

from __future__ import division
import matplotlib.pyplot as plt
import sys
import math
import numpy
import os
import io
import scipy.stats

from simlib.defaults import *
from simlib.models import *

A = (1,1)
B = (2.5,1)
C = (2,2)

# modify from here

# the throughput is the sum of exonential functions
# T = p * mu * greek_PI / AREA * [ COEFFICIENT_1 * exp (-(1-q) * mu * UNION_1) + COEFFICIENT_2 * exp (-(1-q) * mu * UNION_2) + ...]

UNIONS = (math.pi, ) # (UNION_1, UNION_2, ...)
COEFFICIENTS = (3 * math.pi, ) # (COEFFICIENT_1, COEFFICIENT_2, ...)
AREA = 3 * math.pi # AREA

# to here

def postprocessing():
    directory = os.path.abspath(os.path.join('.', DEFAULT.OUTPUT_FOLDER_NAME, 'results-LoRaWAN-sim-3-gw'))
    if not os.path.exists(directory):
        print('this kind of experiment has never been tested')
        return
    else:
        directory_dumps = os.path.abspath(os.path.join(directory, 'dumps'))
        if not os.path.exists(directory_dumps):
            print('no simulation present')
            return
        directory_figures = os.path.abspath(os.path.join(directory, 'figures'))
        try:
            os.makedirs(directory_figures)
        except FileExistsError:
            pass
    
    rate = 1 / DEFAULT.INTERARRIVAL_TIME_MIN
    time_on_air = DEFAULT.TIME_TX_PACKET_MAX
    channels_values = [1, 3]
    duty_cycle_values = [100.0, 1.0]
    L = 1
    colors = [['r', 'g', 'b'], [(1.0, 0.5, 0.5), (0.5, 1.0, 0.5), (0.5, 0.5, 1.0)]]
    dc2label = {100.0: 'No', 1.0: '1%'}
    
    data = getdata(directory = directory_dumps)

    figure = plt.figure()
    
    for enum1, num_channels in enumerate(channels_values):
        p, q = pure_Aloha_model(rate, time_on_air, num_channels)
        for enum2, duty_cycle in enumerate(duty_cycle_values):
            throughput_function = throughput_model(UNIONS, COEFFICIENTS, AREA, p(duty_cycle / 100), q(duty_cycle / 100))
            key = (duty_cycle, num_channels)
            xx = numpy.arange(0, 81, 10)
            if key in data:
                xx = data[key]['xx']
                yy = data[key]['T{}'.format(L)]
                num = numpy.array(data[key]['num'])
                levels = numpy.array([scipy.stats.t.interval(0.95, n - 1)[1] for n in data[key]['num']])
                yyerr = numpy.array(data[key]['E{}'.format(L)]) * levels
                figure.gca().errorbar(xx, yy, yerr=yyerr,
                                    color=colors[enum2][enum1+1],
                                    linestyle=':',
                                    marker = 'o', ms=4, mfc='none',
                                    capsize=2,
                                    label='{} ch, {} DC, sim'.format(num_channels, dc2label[duty_cycle]))
            yy_theory = numpy.vectorize(throughput_function)(xx)
            figure.gca().plot(xx, yy_theory,
                                color=colors[enum2][enum1+1],
                                label='{} ch, {} DC, theory'.format(num_channels, dc2label[duty_cycle]))

    figure.gca().grid()
    figure.gca().legend()
    figure.gca().set_xlabel(r'$\mathrm{Number\/of\/end\/devices\/per\/R^2\/km^2}$', fontsize='x-large')
    figure.gca().set_ylabel(r'$\mathrm{Throughput}$', fontsize='x-large')
    figure.savefig(os.path.abspath(os.path.join(directory_figures, 'throughput_REOC.png')))
    figure.savefig(os.path.abspath(os.path.join(directory_figures, 'throughput_REOC.eps')))
    plt.close(figure)

def getdata(directory):
    list_dir = os.listdir(directory)
    experiments = []
    successful_rx = 3
    for filename in list_dir:
        if 'short' in filename:
            f = io.open(os.path.join(directory, filename), encoding='utf-8')
            lines = f.readlines()
            f.close()
            experiment = []
            for line in lines:
                line = line.strip()
                if line != DEFAULT.SEPARATOR:
                    experiment += [line]
                    continue
                if len(experiment) != 2:
                    print(experiment)
                assert len(experiment) == 2
                experiments += [experiment[:]]
                experiment = []
    data = {}
    for experiment in experiments:
        header, rawdata = experiment
        header = header.split(' ')
        rawdata = rawdata.split(' ')
        seed = int(header[header.index('SEED') + 1])
        assert seed != None

        duty_cycle = float(header[header[header.index('EDCOM'):].index('duty_cycle') + 1 + header.index('EDCOM')])

        density = float(header[header[header.index('EDDEP'):].index('density') + 1 + header.index('EDDEP')])
        
        index_channels = 1
        channels_chunk = header[header[header.index('COM'):].index('channels') + index_channels + header.index('COM')]
        while channels_chunk[-1] != ')':
            index_channels += 1
            channels_chunk += header[header[header.index('COM'):].index('channels') + index_channels + header.index('COM')]
        channels = len(eval(channels_chunk))
        
        duration = float(header[header.index('DURATION') + 1])
        
        width = float(header[header.index('width') + 1])
        
        height = float(header[header.index('height') + 1])
        
        area_simulations = width * height
        
        area_of_relevance = AREA
        
        key = (duty_cycle, channels)
        
        throughput = tuple(float(rawdata[rawdata.index('T{}'.format(i)) + 1]) for i in range(1, successful_rx + 1))
        
        if key not in data:
            data[key] = {}
        if density not in data[key]:
            data[key][density] = {'values': [], 'seeds': [], 'durations': []}
        if seed not in data[key][density]['seeds']:
            data[key][density]['seeds'] += [seed]
            data[key][density]['values'] += [throughput]
            data[key][density]['durations'] += [duration]
        else:
            duration_stored_index = data[key][density]['seeds'].index(seed)
            duration_stored = data[key][density]['durations'][duration_stored_index]
            if duration > duration_stored:
                data[key][density]['values'][duration_stored_index] = throughput
                data[key][density]['durations'][duration_stored_index] = duration

    for key, item in data.items():
        xx = sorted(item.keys())
        t_avg = dict((i + 1, []) for i in range(successful_rx))
        t_err = dict((i + 1, []) for i in range(successful_rx))
        t_num = []
        for x in xx:
            values = numpy.array(item[x]['values']) * area_simulations / area_of_relevance
            avg = numpy.mean(values, axis=0)
            err = scipy.stats.sem(values, axis=0)
            for i in range(successful_rx):
                t_avg[i + 1] += [avg[i]]
                t_err[i + 1] += [err[i]]
            t_num += [len(values)]
        data[key] = {'xx': xx, 'num': t_num}
        for i in range(1, successful_rx + 1):
            data[key]['T{}'.format(i)] = t_avg[i]
            data[key]['E{}'.format(i)] = t_err[i]
    return data

if __name__ == '__main__':
    postprocessing()
