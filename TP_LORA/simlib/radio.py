#!/usr/bin/env python3

from simlib.defaults import *
from simlib.eventscheduler import *
from simlib.receptioncount import *


class Radio(object):
    def __init__(self, channels, device, duty_cycle=DEFAULT.ENDDEVICE.duty_cycle, txonly=False):
        if not isinstance(channels, tuple) or channels == ():
            raise TypeError('channels must be arranged in a tuple and their number cannot be null')
        self.__state = DEFAULT.RADIO.STATE.SLEEP
        self.__outgoing_packet = None
        self.__incoming_packet = None
        self.__receptions = dict([(channel, ReceptionCount(self, channel)) for channel in channels])
        self.__txonly = txonly
        self.__current_channel = None
        self.__device = device
        self.__duty_cycle = duty_cycle
        self.__duty_cycle_active = False
        self.eventscheduler = EventScheduler()

    def is_channel_available(self, channel):
        return channel in self.__receptions.keys()

    def get_fixed_channel(self):
        if len(self.__receptions.keys()) == 1:
            return list(self.__receptions.keys())[0]

    def __set_channel(self, channel):
        assert self.__current_channel is None
        assert channel in self.__receptions.keys() or (len(self.__receptions) == 1 and channel is None)
        self.__current_channel = channel if len(self.__receptions) > 1 else list(self.__receptions.keys())[0]

    def __unset_channel(self):
        assert self.__current_channel is not None
        self.__current_channel = None

    def is_sleep(self):
        return self.__state == DEFAULT.RADIO.STATE.SLEEP

    def can_transmit(self):
        return self.is_sleep() and not self.__duty_cycle_active

    def transmit(self, packet, channel=None):
        assert self.__state == DEFAULT.RADIO.STATE.SLEEP
        assert self.__outgoing_packet is None
        assert not self.__duty_cycle_active
        self.__outgoing_packet = packet
        self.__set_channel(channel)
        self.eventscheduler.schedule_event(packet.get_toa(), self.transmit_completed_cb)
        packet.start_transmission(self.__current_channel)
        self.__state = DEFAULT.RADIO.STATE.TRANSMITTING

    def transmit_completed_cb(self):
        assert self.__state == DEFAULT.RADIO.STATE.TRANSMITTING
        assert self.__outgoing_packet is not None
        packet = self.__outgoing_packet
        self.__outgoing_packet = None
        channel = self.__current_channel
        self.__unset_channel()
        packet.stop_transmission()
        self.__device.transmit_completed_cb(packet, channel)
        self.__duty_cycle_active = True
        self.eventscheduler.schedule_event(packet.get_toa() * (100 / self.__duty_cycle - 1), self.__start_availability)
        self.__state = DEFAULT.RADIO.STATE.SLEEP

    def start_listening(self, channel=None):
        if self.__txonly:
            raise Exception('starting listening on a txonly channel should never happen')
        assert self.__state == DEFAULT.RADIO.STATE.SLEEP
        self.__set_channel(channel)
        self.__state = (DEFAULT.RADIO.STATE.LISTENING
                        if self.__receptions[self.__current_channel].get() == 0
                        else DEFAULT.RADIO.STATE.COLLISION)

    def stop_listening(self):
        if self.__txonly:
            raise Exception('stopping listening on a txonly channel should never happen')
        assert self.__state not in [DEFAULT.RADIO.STATE.SLEEP, DEFAULT.RADIO.STATE.TRANSMITTING]
        self.__incoming_packet = None
        self.__unset_channel()
        self.__state = DEFAULT.RADIO.STATE.SLEEP

    def receive(self, packet, channel):
        if self.__txonly:
            raise Exception('starting receiveing on a txonly channel should never happen')
        self.__receptions[channel].increment(packet.get_toa())
        if self.__current_channel != channel or self.__state == DEFAULT.RADIO.STATE.TRANSMITTING:
            return
        device_id = self.__device.get_attributes().id_device
        packet.start_reception(device_id=device_id)
        if self.__state == DEFAULT.RADIO.STATE.LISTENING:
            assert self.__incoming_packet is None
            self.__incoming_packet = packet
            self.__state = DEFAULT.RADIO.STATE.RECEIVING
        else:
            assert (self.__incoming_packet is not None) == (self.__state == DEFAULT.RADIO.STATE.RECEIVING)
            if self.__incoming_packet is not None:
                self.__incoming_packet.stop_reception(device_id=device_id, outcome=False)
                self.__incoming_packet = None
            packet.stop_reception(device_id=device_id, outcome=False)
            self.__state = DEFAULT.RADIO.STATE.COLLISION

    def receive_completed_cb(self, channel):
        if self.__txonly:
            raise Exception('receiving cannot be completed on a txonly channel')
        if self.__current_channel != channel or self.__state == DEFAULT.RADIO.STATE.TRANSMITTING:
            return
        assert self.__state != DEFAULT.RADIO.STATE.LISTENING
        if self.__state == DEFAULT.RADIO.STATE.RECEIVING:
            assert self.__receptions[channel].get() == 0 and self.__incoming_packet is not None
            self.__incoming_packet.stop_reception(device_id=self.__device.get_attributes().id_device, outcome=True)
        self.__device.receive_completed_cb(self.__incoming_packet, channel)
        self.__incoming_packet = None
        self.__state = DEFAULT.RADIO.STATE.LISTENING if self.__receptions[
                                                            channel].get() == 0 else DEFAULT.RADIO.STATE.COLLISION

    def __start_availability(self):
        assert self.__duty_cycle_active
        self.__duty_cycle_active = False
        self.__device.start_availability_cb()
