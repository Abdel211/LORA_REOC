#!/usr/bin/env python3

import threading
import io

from simlib.borg import *
from simlib.eventscheduler import *
from simlib.defaults import *


class Monitor(Borg):
    ''' Public Borg methods to be defined in subclasses '''

    def init(self, file_name=None, long_file_enabled=True):
        if self.master_exists() and not self.is_master():
            raise AttributeError('a bug is present, this must never happen')
        if file_name is None:
            if self.master_exists():
                self.reset()
                raise ValueError('master cannot be set without specifying a duration')
            return
        self.set_master()
        self.event_scheduler = EventScheduler()

        self.__file_name = file_name
        self.__long_file_enabled = long_file_enabled
        self.__stop_condition = threading.Event()
        self.__lock = threading.Lock()
        self.__queue = []
        self.__thread = threading.Thread(target=self.__run)
        self.__thread.start()

    ''' Public methods '''

    def log(self, log_message, long_file=True, short_file=False, timestamp=False):
        if not self.master_exists():
            raise AttributeError('this method cannot be called if a master does not exist')
        self.__lock.acquire()
        log_message = '{} '.format(self.event_scheduler.get_current_time()) * timestamp + log_message
        self.__queue.append((log_message, long_file and self.__long_file_enabled, short_file))
        self.__lock.release()

    def logline(self, log_message, *args, **kwargs):
        self.log(log_message + '\n', *args, **kwargs)

    def reset(self):
        if self.is_master():
            self.__stop_condition.set()
            self.__thread.join()
            self.__stop_condition.clear()
        super(Monitor, self).reset()

    ''' Private helper methods'''

    def __run(self):
        while not self.__stop_condition.is_set():
            self.__stop_condition.wait(100)
            dump_long = ''
            dump_short = ''
            self.__lock.acquire()
            for string_to_write, long_file, short_file in self.__queue:
                dump_long += long_file * string_to_write
                dump_short += short_file * string_to_write
            self.__queue.clear()
            self.__lock.release()
            if self.__stop_condition.is_set():
                if self.__long_file_enabled:
                    dump_long += DEFAULT.SEPARATOR + '\n'
                dump_short += DEFAULT.SEPARATOR + '\n'
            if dump_long != '' and self.__long_file_enabled:
                with io.open(self.__file_name + '_long.txt', 'a', encoding='utf-8') as f:
                    f.write(dump_long.encode().decode())
            if dump_short != '':
                with io.open(self.__file_name + '_short.txt', 'a', encoding='utf-8') as f:
                    f.write(dump_short.encode().decode())
