#!/usr/bin/env python3

from simlib.defaults import *


class BufferOverflow(Exception):
    pass


class Buffer(object):
    def __init__(self, bufsize=DEFAULT.BUFFER.SIZE):
        self.__bufsize = bufsize
        self.__queue = []

    def enqueue(self, packet):
        if self.__bufsize != 0:
            if len(self.__queue) == self.__bufsize:
                raise BufferOverflow()
        self.__queue.append(packet)

    def select(self, condition=DEFAULT.BUFFER.SELECTCONDITION):
        if not callable(condition):
            raise TypeError('condition must be a function')
        if condition.__code__.co_argcount != 1:
            raise TypeError('condition function must take 1 argument')
        for packet in self.__queue:
            if condition(packet):
                return packet

    def dequeue(self, packet):
        self.__queue.remove(packet)
