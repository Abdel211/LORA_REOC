#!/usr/bin/env python3

import numpy
import random

from simlib.borg import *


class Randomness(Borg):
    def init(self, seed=None):
        if self.master_exists():
            if not self.is_master():
                raise AttributeError('a bug is present, this must never happen')
        elif seed is None:
            return
        else:
            self.set_master()
        self.__predefined_random = random.Random(seed)
        self.__predefined_numpy_random = numpy.random.RandomState(seed)
        self.__runtime_random = random.Random(seed)
        self.__runtime_numpy_random = numpy.random.RandomState(seed)

    def get_predefined_random(self):
        if not self.master_exists():
            raise AttributeError('this method cannot be called if a master does not exist')
        return self.__predefined_random

    def get_predefined_numpy_random(self):
        if not self.master_exists():
            raise AttributeError('this method cannot be called if a master does not exist')
        return self.__predefined_numpy_random

    def get_runtime_random(self):
        if not self.master_exists():
            raise AttributeError('this method cannot be called if a master does not exist')
        return self.__runtime_random

    def get_runtime_numpy_random(self):
        if not self.master_exists():
            raise AttributeError('this method cannot be called if a master does not exist')
        return self.__runtime_numpy_random
