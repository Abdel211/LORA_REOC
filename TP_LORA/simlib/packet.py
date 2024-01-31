#!/usr/bin/env python3

from simlib.defaults import *
from simlib.eventscheduler import *
from simlib.monitor import *


class Packet(object):
    def __init__(self, serial, device, toa):
        self.__serial = serial
        self.__device = device
        self.__toa = toa
        self.__retransmissions = {}
        self.__reset()
        self.__delivery_finished = False
        self.eventscheduler = EventScheduler()
        self.monitor = Monitor()

    def get_serial(self):
        return self.__serial

    def get_toa(self):
        return self.__toa

    def get_sender(self):
        return self.__device

    def get_receptions(self):
        return self.__receptions

    def is_not_handled(self):
        return self.__waiting

    def delivery_finished(self):
        return self.__delivery_finished

    def start_transmission(self, channel):
        # called by radio
        assert channel is not None
        assert self.__transmission is None
        assert self.__receptions is None
        self.__delivery_finished = False
        self.__transmission = {DEFAULT.PACKET.STARTTX: self.eventscheduler.get_current_time(),
                               DEFAULT.PACKET.CHANNEL: channel, DEFAULT.PACKET.STOPTX: None}
        self.__waiting = False
        self.__receptions = {}

    def stop_transmission(self):
        # called by radio
        assert self.__transmission is not None
        assert self.__transmission[DEFAULT.PACKET.STOPTX] is None
        self.__transmission[DEFAULT.PACKET.STOPTX] = self.eventscheduler.get_current_time()
        if all(value[DEFAULT.PACKET.STOPRX] is not None for value in self.__receptions.values()):
            self.__delivery_finished = True

    def start_reception(self, device_id):
        # called by radio
        assert self.__transmission is not None
        self.__receptions[device_id] = {DEFAULT.PACKET.STARTRX: self.eventscheduler.get_current_time(),
                                        DEFAULT.PACKET.OUTCOME: None, DEFAULT.PACKET.STOPRX: None}

    def stop_reception(self, device_id, outcome):
        # called by radio
        assert type(outcome) == bool
        assert self.__receptions is not None
        assert device_id in self.__receptions
        assert self.__receptions[device_id][DEFAULT.PACKET.OUTCOME] is None
        assert self.__receptions[device_id][DEFAULT.PACKET.STOPRX] is None
        self.__receptions[device_id][DEFAULT.PACKET.OUTCOME] = outcome
        self.__receptions[device_id][DEFAULT.PACKET.STOPRX] = self.eventscheduler.get_current_time()
        if (all(value[DEFAULT.PACKET.STOPRX] is not None for value in self.__receptions.values())
                and self.__transmission[DEFAULT.PACKET.STOPTX] is not None):
            self.__delivery_finished = True

    def enable_retransmission(self):
        # do not use this method by now
        if not any(value[DEFAULT.PACKET.OUTCOME] for value in self.__receptions.values()):
            nbr_retransmissions = len(self.__retransmissions)
            self.__retransmissions[nbr_retransmission] = {}
            self.__retransmissions[nbr_retransmission][DEFAULT.PACKET.TX] = dict(self.__transmission)
            self.__retransmissions[nbr_retransmission][DEFAULT.PACKET.RX] = dict(self.__receptions)
            self.__reset()

    def __reset(self):
        self.__waiting = True
        self.__transmission = None
        self.__receptions = None
