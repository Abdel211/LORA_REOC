#!/usr/bin/env python3

import os
import time

from simlib.eventscheduler import *
from simlib.monitor import *
from simlib.deployment import *
from simlib.randomness import *


class Experiment(object):
    def __init__(self, duration, seed=None, root_directory=DEFAULT.ROOT_DIRECTORY,
                 results_dirname='results-LoRaWAN-sim', execution_id=None, randomness=None,
                 long_file_enabled=True):
        self.event_scheduler = EventScheduler(duration=duration)
        directory = os.path.abspath(os.path.join(root_directory, DEFAULT.OUTPUT_FOLDER_NAME, results_dirname))
        directory_dumps = os.path.abspath(os.path.join(directory, 'dumps'))
        if not os.path.exists(directory_dumps):
            try:
                os.makedirs(directory_dumps)
            except FileExistsError:
                # Can have meanwhile been created by a concurrent process
                pass
        self.__directory_figures = os.path.abspath(os.path.join(directory, 'figures'))
        if not os.path.exists(self.__directory_figures):
            try:
                os.makedirs(self.__directory_figures)
            except FileExistsError:
                # Can have meanwhile been created by a concurrent process
                pass

        if execution_id is None:
            execution_id = int(time.time())
        self.__execution_id = execution_id
        self.monitor = Monitor(os.path.join(directory_dumps, 'dump_{}'.format(str(self.__execution_id))), long_file_enabled)
        self.monitor.log('@EXPERIMENT {}DURATION {} '.format('SEED {} '.format(seed) if seed is not None else '',
                                                             duration),
                         True, True)
        self.deployment = Deployment()
        self.__flag_home_randomness = False
        if randomness is None:
            self.__flag_home_randomness = True
            randomness = Randomness(master=True, seed=seed)
        self.randomness = randomness

    def run(self, relaxed=False, verbose=False):
        self.deployment.prepare()
        self.deployment.start()
        flag = False
        try:
            self.event_scheduler.run(verbose=verbose)
        except KeyboardInterrupt:
            print('stopped while running experiment')
            flag = True
        else:
            self.deployment.save_stats(relaxed)
        finally:
            self.event_scheduler.reset()
            self.monitor.reset()
            if self.__flag_home_randomness:
                self.randomness.reset()
            if flag:
                raise KeyboardInterrupt()

    def plot(self, filename=None, **kwargs):
        if filename is None:
            filename = 'map_{}'.format(self.__execution_id)
        path_to_plot = os.path.abspath(os.path.join(self.__directory_figures, filename))
        self.deployment.plot(filename=path_to_plot, **kwargs)
    
    def isfile(self, filename):
        path_to_plot = os.path.abspath(os.path.join(self.__directory_figures, filename))
        return os.path.isfile('{}.eps'.format(path_to_plot)) or os.path.isfile('{}.png'.format(path_to_plot))
