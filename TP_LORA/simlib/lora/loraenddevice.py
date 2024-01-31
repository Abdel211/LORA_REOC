#!/usr/bin/env python3

from __future__ import division
from simlib.device import *
from simlib.randomness import *
from simlib.radio import *
from simlib.packet import *


class LoRaEndDevice(Device):
    def __init__(self, *args, **kwargs):
        self.eventscheduler = EventScheduler()
        self.__interarrival_time = kwargs.pop('interarrival_time', DEFAULT.ENDDEVICE.interarrival_time)
        self.__time_tx_packet = kwargs.pop('time_tx_packet', DEFAULT.ENDDEVICE.time_tx_packet)
        self.__duty_cycle = kwargs.pop('duty_cycle', DEFAULT.ENDDEVICE.duty_cycle)
        self.__backlog_until_end_of_duty_cycle = kwargs.pop('backlog_until_end_of_duty_cycle',
                                                            DEFAULT.ENDDEVICE.backlog_until_end_of_duty_cycle)
        self.__packet_count = 0
        self.monitor = Monitor()
        self.statistics = {'GEN': 0.0, 'TX': 0.0, 'RX': {}, 'D': {}}
        super(LoRaEndDevice, self).__init__(*args, **kwargs)

    def start(self):
        super(LoRaEndDevice, self).start()
        self.__schedule_generate()

    def setup_radios(self):
        channels = tuple(list(self.get_attributes().channels) + [869.75])
        radio = Radio(channels=channels, device=self, duty_cycle=self.__duty_cycle)
        self.add_radio(radio)

    def reset(self, interarrival_time=None, time_tx_packet=None, duty_cycle=None, bufsize=None, **kwargs):
        super(LoRaEndDevice, self).reset(**kwargs)
        self.__interarrival_time = self.__interarrival_time if interarrival_time is None else interarrival_time
        self.__time_tx_packet = self.__time_tx_packet if time_tx_packet is None else time_tx_packet
        self.__duty_cycle = self.__duty_cycle if duty_cycle is None else duty_cycle
        self.statistics = {'GEN': 0.0, 'TX': 0.0, 'RX': {}, 'D': {}}

    def generate(self):
        log_message = 'G {}'.format(self.get_attributes().id_device)
        self.monitor.logline(log_message, timestamp=True)
        self.statistics['GEN'] += 1
        packet = Packet(serial=self.__packet_count, device=self, toa=self.__time_tx_packet)
        self.__packet_count += 1
        try:
            self.enqueue_transmitting_packet(packet)
        except BufferOverflow:
            pass
        else:
            self.transmit()
        self.__schedule_generate()

    def transmit(self, packet=None, condition=DEFAULT.BUFFER.SELECTCONDITION, channel=None, radio=None):
        packet = self.select_transmitting_packet(condition=lambda packet: packet.is_not_handled())
        if packet is None:
            return
        if not self.can_transmit():
            log_message = 'P {}'.format(self.get_attributes().id_device)
            self.monitor.logline(log_message, timestamp=True)
            return
        channel, = Randomness().get_runtime_random().sample(self.get_attributes().channels, 1)
        super(LoRaEndDevice, self).transmit(packet=packet, channel=channel)
        log_message = 'B {} {}'.format(self.get_attributes().id_device, channel)
        self.monitor.logline(log_message, timestamp=True)
        self.statistics['TX'] += 1

    def transmit_completed_cb(self, packet, channel):
        super(LoRaEndDevice, self).transmit_completed_cb(packet=packet, channel=channel)
        if packet.delivery_finished():
            self.log_end_of_transmission(packet)
        if not self.__backlog_until_end_of_duty_cycle:
            self.dequeue_transmitted_packet(packet)

    def start_availability_cb(self):
        if self.__backlog_until_end_of_duty_cycle:
            packet = self.select_transmitting_packet(condition=lambda packet: not packet.is_not_handled())
            assert packet is not None
            self.dequeue_transmitted_packet(packet)
        log_message = 'A {}'.format(self.get_attributes().id_device)
        self.monitor.logline(log_message, timestamp=True)
        self.transmit()

    def log_end_of_transmission(self, packet):
        log_message = 'E {}'.format(self.get_attributes().id_device)
        successes = 0
        for id_device, reception in packet.get_receptions().items():
            if reception[DEFAULT.PACKET.OUTCOME]:
                log_message += ' {}'.format(id_device)
                successes += 1
        self.monitor.logline(log_message, timestamp=True)
        current_time = self.eventscheduler.get_current_time()
        for success in range(1, successes + 1):
            if not success in self.statistics['RX']:
                self.statistics['RX'][success] = 0.0
            self.statistics['RX'][success] += 1
            if current_time is None:
                continue
            if success not in self.statistics['D']:
                self.statistics['D'][success] = []
            else:
                assert len(self.statistics['D'][success]) >= 1
                previous_time = self.statistics['D'][success].pop()
                self.statistics['D'][success] += [current_time - previous_time]
            self.statistics['D'][success] += [current_time]

    def get_attributes(self):
        obj = super(LoRaEndDevice, self).get_attributes()
        obj.interarrival_time = self.__interarrival_time
        obj.time_tx_packet = self.__time_tx_packet
        obj.duty_cycle = self.__duty_cycle
        return obj

    def __schedule_generate(self):
        time_generation = Randomness().get_predefined_random().expovariate(1 / self.__interarrival_time)
        self.eventscheduler.schedule_event(time_generation, self.generate)
