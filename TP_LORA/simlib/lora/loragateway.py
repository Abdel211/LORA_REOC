#!/usr/bin/env python3

from __future__ import division
from simlib.device import *
from simlib.radio import *
from simlib.packet import *


class LoRaGateway(Device):
    def __init__(self, *args, **kwargs):
        self.__duty_cycle = kwargs.pop('duty_cycle', DEFAULT.GATEWAY.duty_cycle)
        super(LoRaGateway, self).__init__(*args, **kwargs)

    def start(self):
        super(LoRaGateway, self).start()
        for channel in self.get_attributes().channels:
            self.start_listening(channel=channel)

    def setup_radios(self):
        for channel in self.get_attributes().channels:
            radio = Radio(channels=(channel,), device=self, duty_cycle=self.__duty_cycle)
            self.add_radio(radio)
        radio = Radio(channels=(869.75,), device=self, txonly=True, duty_cycle=self.__duty_cycle)
        self.add_radio(radio)

    def receive_completed_cb(self, packet, channel):
        if packet is not None and packet.delivery_finished():
            packet.get_sender().log_end_of_transmission(packet)
