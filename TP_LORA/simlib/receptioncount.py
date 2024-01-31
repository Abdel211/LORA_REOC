#!/usr/bin/env python3

from simlib.eventscheduler import *


class ReceptionCount(object):
    def __init__(self, radio, channel):
        self.__value = 0
        self.__radio = radio
        self.__channel = channel
        self.eventscheduler = EventScheduler()

    def increment(self, toa):
        self.__value += 1
        self.eventscheduler.schedule_event(toa, self.__decrement)

    def __decrement(self):
        assert self.__value > 0
        self.__value -= 1
        self.__radio.receive_completed_cb(self.__channel)

    def get(self):
        return self.__value
