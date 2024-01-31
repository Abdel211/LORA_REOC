#!/usr/bin/env python3

from __future__ import division
import bisect
import time

from simlib.borg import *


class EventScheduler(Borg):
    ''' Public Borg methods to be defined in subclasses '''

    def init(self, duration=None):
        if self.master_exists() and not self.is_master():
            raise AttributeError('a bug is present, this must never happen')
        if duration is None:
            if self.master_exists():
                self.reset()
                raise ValueError('master cannot be set without specifying a duration')
            return
        self.set_master()
        self.__duration = duration
        self.__current_time = 0
        self.__list_event_time = []

    ''' Public methods '''

    def run(self, verbose=False):
        if not self.is_master():
            raise AttributeError('this method can only be called by the master')
        compare_time = time.time()
        while (self.__list_event_time != []) and (self.__list_event_time[0][0] <= self.__duration):
            event_time, function = self.__list_event_time.pop(0)
            assert event_time >= self.__current_time
            if verbose:
                now = int(event_time * 10 / self.__duration)
                earlier = int(self.__current_time * 10 / self.__duration)
                if now > earlier:
                    speed = event_time / (time.time() - compare_time)
                    print(now * 10, '%')
                    print('\tspeed\t\t\t{}'.format(speed))
                    remaining_time = (self.__duration - event_time) / speed
                    print('\testimated end in\t{}m{}s'.format(int(remaining_time) // 60, remaining_time % 60))
                    print('\tevents in queue\t\t{}'.format(len(self.__list_event_time)))
            self.__current_time = event_time
            function()

    def schedule_event(self, time_interval, function):
        if not self.master_exists():
            raise AttributeError('this method cannot be called if a master does not exist')
        absolute_time = self.__current_time + time_interval
        if self.__duration is None or absolute_time <= self.__duration:
            starting_index = bisect.bisect(self.__list_event_time, (absolute_time,))
            index_to_add = 0
            for index_to_add, item in enumerate(self.__list_event_time[starting_index:]):
                if absolute_time != item[0]:
                    break
            self.__list_event_time.insert(starting_index + index_to_add, (absolute_time, function))
            # ~ bisect.insort(self.__list_event_time, (absolute_time, function))

    def get_current_time(self):
        if not self.master_exists():
            raise AttributeError('this method cannot be called if a master does not exist')
        return self.__current_time

    def get_duration(self):
        if not self.master_exists():
            raise AttributeError('this method cannot be called if a master does not exist')
        return self.__duration
