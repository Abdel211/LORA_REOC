#!/usr/bin/env python3

import math

from simlib.defaults import *
from simlib.radio import *
from simlib.buffer import *


class Device(object):
    def __init__(self, id_device, x, y,
                 coverage_range=DEFAULT.DEVICE.COMMON.coverage_range,
                 channels=DEFAULT.DEVICE.COMMON.channels,
                 output_bufsize=DEFAULT.DEVICE.OPTIONAL.output_bufsize,
                 input_bufsize=DEFAULT.DEVICE.OPTIONAL.input_bufsize):
        # INHERIT this method in subclasses of Device
        self.__id_device = id_device
        self.__x = x
        self.__y = y
        self.connections = set()
        self.incoming_connections = set()
        if coverage_range is None:
            raise TypeError('coverage range cannot be None')
        if channels is None:
            raise TypeError('channels cannot be None')
        if output_bufsize is None:
            raise TypeError('output bufsize cannot be None')
        if input_bufsize is None:
            raise TypeError('input bufsize cannot be None')
        self.__reset(coverage_range=coverage_range, channels=channels, output_bufsize=output_bufsize,
                     input_bufsize=input_bufsize)
        
    # Overload comparison operator to enable device sorting
    def __lt__(self, other):
        return self.__id_device < other.get_attributes().id_device

    def start(self):
        # INHERIT this method in subclasses of Device
        self.__output_buffer = Buffer(self.__output_bufsize)
        self.__input_buffer = Buffer(self.__input_bufsize)
        self.__radios = set()
        self.setup_radios()

    def setup_radios(self):
        # OVERRIDE this method in subclasses of Device
        radio = Radio(channels=self.__channels, device=self)
        self.add_radio(radio)

    def add_radio(self, radio):
        self.__radios.add(radio)

    def reset(self, **kwargs):
        # INHERIT this method in subclasses of Device
        self.__reset(**kwargs)

    def connect(self, neighbor):
        distance = math.sqrt(
            (self.__x - neighbor.get_attributes().x) ** 2 + (self.__y - neighbor.get_attributes().y) ** 2)
        if distance <= self.__coverage_range:
            self.connections.add(neighbor)
            neighbor.incoming_connections.add(self)
        if distance <= neighbor.get_attributes().coverage_range:
            neighbor.connections.add(self)
            self.incoming_connections.add(neighbor)

    def disconnect(self):
        for neighbor in self.connections:
            neighbor.incoming_connections.remove(self)
        self.connections.clear()
        for neighbor in self.incoming_connections:
            neighbor.connections.remove(self)
        self.incoming_connections.clear()

    def get_neighbors(self):
        return self.connections

    def enqueue_transmitting_packet(self, packet):
        self.__output_buffer.enqueue(packet)

    def select_transmitting_packet(self, condition=DEFAULT.BUFFER.SELECTCONDITION):
        return self.__output_buffer.select(condition)

    def dequeue_transmitted_packet(self, packet):
        self.__output_buffer.dequeue(packet)

    def enqueue_receiving_packet(self, packet):
        self.__input_buffer.enqueue(packet)

    def select_receiving_packet(self, condition=DEFAULT.BUFFER.SELECTCONDITION):
        return self.__input_buffer.select(condition)

    def dequeue_received_packet(self, packet):
        self.__input_buffer.dequeue(packet)

    def can_transmit(self, channel=None):
        return self.__get_radio(channel).can_transmit()

    def transmit(self, packet=None, condition=DEFAULT.BUFFER.SELECTCONDITION, channel=None, radio=None):
        # INHERIT this method in subclasses of Device
        if radio == None:
            radio = self.__get_radio(channel)
        else:
            radio_channel = radio.get_fixed_channel()
            if radio_channel is None:
                assert channel is not None
            else:
                if channel is None:
                    channel = radio_channel
                assert radio_channel == channel
        if not radio.can_transmit():
            return
        if packet == None:
            packet = self.select_transmitting_packet(condition)
            if packet == None:
                return
        radio.transmit(packet, channel)
        for neighbor in self.get_neighbors():
            neighbor.receive(packet, channel)

    def transmit_completed_cb(self, packet, channel):
        # INHERIT this method in subclasses of Device
        assert packet is not None
        assert channel is not None

    def start_availability_cb(self):
        # OVERRIDE this method in subclasses of Device
        pass

    def start_listening(self, channel):
        radio = self.__get_radio(channel)
        assert radio is not None
        radio.start_listening(channel)

    def stop_listening(self, channel):
        radio = self.__get_radio(channel)
        assert radio is not None
        radio.stop_listening()

    def receive(self, packet, channel):
        # INHERIT this method in subclasses of Device
        assert packet is not None
        assert channel is not None
        radio = self.__get_radio(channel)
        if radio is None:
            return
        radio.receive(packet, channel)

    def receive_completed_cb(self, packet, channel):
        # OVERRIDE or INHERIT this method in subclasses of Device
        if packet is not None:
            self.enqueue_receiving_packet(packet)

    def get_attributes(self):
        obj = lambda: None
        obj.id_device = self.__id_device
        obj.x = self.__x
        obj.y = self.__y
        obj.coverage_range = self.__coverage_range
        obj.channels = self.__channels
        obj.output_bufsize = self.__output_bufsize
        obj.input_bufsize = self.__input_bufsize
        return obj

    def __reset(self, coverage_range=None, channels=None, output_bufsize=None, input_bufsize=None):
        if coverage_range is not None:
            if not coverage_range:
                raise ValueError('coverage range cannot be null')
            self.__coverage_range = coverage_range
        if channels is not None:
            if not isinstance(channels, tuple) or channels == ():
                raise TypeError('channels must be arranged in a tuple and their number cannot be null')
            self.__channels = channels
        if output_bufsize is not None:
            self.__output_bufsize = output_bufsize
        if input_bufsize is not None:
            self.__input_bufsize = input_bufsize

    def __get_radio(self, channel=None):
        if channel is None:
            assert len(self.__radios) == 1
            return list(self.__radios)[0]
        for radio in self.__radios:
            if radio.is_channel_available(channel):
                return radio
