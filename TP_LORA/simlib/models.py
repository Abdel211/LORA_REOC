#!/usr/bin/env python3

from __future__ import division
import matplotlib.pyplot as plt
import sys
import math
import numpy
import os
import io

from simlib.defaults import *

DEPLOYMENTS = {
    DEFAULT.DEPLOYMENT.SQUARE: {
        1: {
            DEFAULT.SIDE: math.sqrt(2),
            DEFAULT.AREA: 2,
            DEFAULT.UNIONS: (
                math.pi,
                1.5 * math.pi + 1
            ),
            DEFAULT.COEFFICIENTS: {
                1: (
                    math.pi,
                    2 - math.pi
                )
            }
        },
        2: {
            DEFAULT.SIDE: 1,
            DEFAULT.AREA: 1,
            DEFAULT.UNIONS: (
                math.pi,
                4 * math.pi / 3 + 0.5 * math.sqrt(3),
                1.5 * math.pi + 1,
                19 * math.pi / 12 + 0.5 * math.sqrt(3) + 1,
                5 * math.pi / 3 + math.sqrt(3) + 1
            ),
            DEFAULT.COEFFICIENTS: {
                1: (
                    math.pi,
                    math.sqrt(3) - 4 * math.pi / 3,
                    2 - math.pi,
                    5 * math.pi / 3 - 2 * math.sqrt(3),
                    math.sqrt(3) - math.pi / 3 - 1
                ),
                2: (
                    0,
                    4 * math.pi / 3 - math.sqrt(3),
                    math.pi - 2,
                    4 * math.sqrt(3) - 10 * math.pi / 3,
                    math.pi - 3 * math.sqrt(3) + 3
                ),
            }
        },
        3: {
            DEFAULT.SIDE: 0.4 * math.sqrt(5),
            DEFAULT.AREA: 0.8,
            DEFAULT.UNIONS: (
                math.pi,  # U1
                0.8 + math.pi + 2 * math.atan(2),  # U21
                0.4 * math.sqrt(6) + 2 * math.pi - 2 * math.atan(0.5 * math.sqrt(6)),  # U22
                0.8 + 2 * math.pi - 2 * math.atan(2),  # U23
                1.6 + 3 * math.pi - 4 * math.atan(2),  # U31
                1.2 + 0.2 * math.sqrt(6) + 2.5 * math.pi - 2 * math.atan(2) - math.atan(0.5 * math.sqrt(6)),  # U32
                1.2 + 0.4 * math.sqrt(6) + 2 * math.pi + 2 * math.atan(2) - 2 * math.atan(0.5 * math.sqrt(6)),  # U33
                2.4 + 3 * math.pi - 4 * math.atan(2),  # U41
                1.6 + 0.4 * math.sqrt(6) + 3 * math.pi - 2 * math.atan(2) - 2 * math.atan(0.5 * math.sqrt(6)),  # U42
                1.6 + 0.8 * math.sqrt(6) + 3 * math.pi - 4 * math.atan(0.5 * math.sqrt(6))  # U43 #check
            ),
            DEFAULT.COEFFICIENTS: {
                1: (
                    math.pi,
                    - (-1.6 + 2 * math.pi - 4 * math.atan(2)),
                    - (-0.8 * math.sqrt(6) + 4 * math.atan(0.5 * math.sqrt(6))),
                    - (-1.6 + 4 * math.atan(2)),
                    -1.6 + 2 * math.pi - 4 * math.atan(2),
                    -1.6 - 0.8 * math.sqrt(6) - 2 * math.pi + 8 * math.atan(2) + 4 * math.atan(0.5 * math.sqrt(6)),
                    1.6 - 1.6 * math.sqrt(6) - 4 * math.atan(2) + 8 * math.atan(0.5 * math.sqrt(6)),
                    - (-0.8 - math.pi + 4 * math.atan(2)),
                    - (1.6 - 1.6 * math.sqrt(6) - 4 * math.atan(2) + 8 * math.atan(0.5 * math.sqrt(6))),
                    0
                ),
                2: (
                    0,
                    -1.6 + 2 * math.pi - 4 * math.atan(2),
                    -0.8 * math.sqrt(6) + 4 * math.atan(0.5 * math.sqrt(6)),
                    -1.6 + 4 * math.atan(2),
                    -2 * (-1.6 + 2 * math.pi - 4 * math.atan(2)),
                    -2 * (-1.6 - 0.8 * math.sqrt(6) - 2 * math.pi + 8 * math.atan(2) + 4 * math.atan(
                        0.5 * math.sqrt(6))),
                    -2 * (1.6 - 1.6 * math.sqrt(6) - 4 * math.atan(2) + 8 * math.atan(0.5 * math.sqrt(6))),
                    3 * (-0.8 - math.pi + 4 * math.atan(2)),
                    3 * (1.6 - 1.6 * math.sqrt(6) - 4 * math.atan(2) + 8 * math.atan(0.5 * math.sqrt(6))),
                    - (1.6 - 0.8 * math.sqrt(6) - math.pi + 4 * math.atan(0.5 * math.sqrt(6)))
                ),
                3: (
                    0,
                    0,
                    0,
                    0,
                    -1.6 + 2 * math.pi - 4 * math.atan(2),
                    -1.6 - 0.8 * math.sqrt(6) - 2 * math.pi + 8 * math.atan(2) + 4 * math.atan(0.5 * math.sqrt(6)),
                    1.6 - 1.6 * math.sqrt(6) - 4 * math.atan(2) + 8 * math.atan(0.5 * math.sqrt(6)),
                    -3 * (-0.8 - math.pi + 4 * math.atan(2)),
                    -3 * (1.6 - 1.6 * math.sqrt(6) - 4 * math.atan(2) + 8 * math.atan(0.5 * math.sqrt(6))),
                    3 * (1.6 - 0.8 * math.sqrt(6) - math.pi + 4 * math.atan(0.5 * math.sqrt(6)))
                ),
            }
        },
    },
    DEFAULT.DEPLOYMENT.HONEYCOMB: {
        1: {
            DEFAULT.SIDE: math.sqrt(3),
            DEFAULT.AREA: 0.75 * math.sqrt(3),
            DEFAULT.UNIONS: (
                math.pi,
                5 * math.pi / 3 + 0.5 * math.sqrt(3)
            ),
            DEFAULT.COEFFICIENTS: {
                1: (
                    0.5 * math.pi,
                    0.75 * math.sqrt(3) - 0.5 * math.pi
                )
            }
        },
        3: {
            DEFAULT.SIDE: 1,
            DEFAULT.AREA: 0.25 * math.sqrt(3),
            DEFAULT.UNIONS: (
                math.pi,
                4 * math.pi / 3 + 0.5 * math.sqrt(3),
                5 * math.pi / 3 + 0.5 * math.sqrt(3),
                1.5 * math.pi + math.sqrt(3),
                5 * math.pi / 3 + math.sqrt(3),
                5 * math.pi / 3 + 1.5 * math.sqrt(3)
            ),
            DEFAULT.COEFFICIENTS: {
                1: (
                    0.5 * math.pi,
                    0.75 * math.sqrt(3) - math.pi,
                    0.75 * math.sqrt(3) - 0.5 * math.pi,
                    0.5 * math.pi - 0.5 * math.sqrt(3),
                    math.pi - 1.5 * math.sqrt(3),
                    0.75 * math.sqrt(3) - 0.5 * math.pi
                ),
                2: (
                    0,
                    math.pi - 0.75 * math.sqrt(3),
                    0.5 * math.pi - 0.75 * math.sqrt(3),
                    math.sqrt(3) - math.pi,
                    3 * math.sqrt(3) - 2 * math.pi,
                    1.5 * math.pi - 2.25 * math.sqrt(3)
                ),
                3: (
                    0,
                    0,
                    0,
                    0.5 * math.pi - 0.5 * math.sqrt(3),
                    math.pi - 1.5 * math.sqrt(3),
                    2.25 * math.sqrt(3) - 1.5 * math.pi
                ),
            }
        },
    },
    DEFAULT.DEPLOYMENT.SINGLE: {
        1: {
            DEFAULT.AREA: math.pi,
            DEFAULT.UNIONS: (
                math.pi,
            ),
            DEFAULT.COEFFICIENTS: {
                1: (
                    math.pi,
                )
            }
        },
    },
}


def pure_Aloha_model(rate, time_on_air, channels):
    x = rate * time_on_air

    def p_function(duty_cycle=1):
        eps = 1 / duty_cycle
        return x / (1 + eps * x)

    def q_function(duty_cycle=1):
        eps = 1 / duty_cycle
        min2eps = min(eps, 2)
        num = min2eps * x - math.exp(-x) + math.exp(x * (1 - min2eps))
        den = channels * (1 + eps * x)
        return 1 - num / den

    return p_function, q_function


def throughput_model_single(*args):
    unions = (math.pi,)
    coefficients = (math.pi,)
    area = math.pi
    return throughput_model(unions, coefficients, area, *args)


def throughput_model_regular(grid_type, minimum_coverage, L, *args):
    deployment = DEPLOYMENTS[grid_type][minimum_coverage]
    unions = deployment[DEFAULT.UNIONS]
    coefficients = deployment[DEFAULT.COEFFICIENTS][L]
    area = deployment[DEFAULT.AREA]
    return throughput_model(unions, coefficients, area, *args)


def throughput_model(unions, coefficients, area, p, q):
    assert len(unions) == len(coefficients)

    def throughput_function(density):
        throughput_value = 0
        for index in range(len(unions)):
            exp_func = math.exp(-(1 - q) * density * unions[index])
            throughput_value += coefficients[index] * exp_func
        throughput_value *= p * density * math.pi / area
        return throughput_value

    return throughput_function
