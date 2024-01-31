#!/usr/bin/env python3

import numpy

from simlib.deployment import *
from simlib.experiment import *
from simlib.defaults import *


def lorawan_sim():
    time_id = int(time.time())
    channels_values = [1, 3]
    duty_cycle_values = [100.0, 1.0]
    densities_values = numpy.arange(0, 81, 5)
    
    # modify from here
    
    seeds = [172832539,
             180175907,
             76988325,
             79139770,
            ] # seeds used to feed the pseudo-random number generator, simulate different scenarios, and achieve statistical significance
    
    duration = 80*10 # duration of each simulation in seconds
    
    # to here
    
    deployment = Deployment.gateway_infrastructure(
                                                    width=3.5, # width of the simulation area (in units of distance, i.e., the coverage radius, which is long 1) : it should be large enough to account for all coverage areas 
                                                    height=3, # height of the simulation area (in units of distance, i.e., the coverage radius, which is long 1): it should be large enough to account for all coverage areas 
                                                    grid=[ # each line should contain the coordinates (in units of distance, i.e., the coverage radius, which is long 1) of a gateway within the area: the related disk should be into the coverage area  
                                                            (1, 1), 
                                                            (2.5, 1), 
                                                            (2, 2)
                                                    ]
    )
    
    for num_channels in channels_values:
        deployment.reset_gateways(channels=tuple(range(num_channels)))
        for density in densities_values:
            for duty_cycle in duty_cycle_values:
                for seed in seeds:
                    print('-------------------> Channels {}, Density {}, Duty Cycle {}, Seed {}'.format(num_channels,
                                                                                                        density,
                                                                                                        duty_cycle,
                                                                                                        seed))
                    e = Experiment(duration=duration,
                                    seed=seed, 
                                    execution_id=time_id,
                                    results_dirname='results-LoRaWAN-sim-3-gw', 
                                    long_file_enabled=False)

                    deployment.poisson_end_device_infrastructure(density=density,
                                                                 interarrival_time=DEFAULT.INTERARRIVAL_TIME_MIN,
                                                                 time_tx_packet=DEFAULT.TIME_TX_PACKET_MAX,
                                                                 duty_cycle=duty_cycle,
                                                                 output_bufsize=1,
                                                                 backlog_until_end_of_duty_cycle=True)
                    # ~ plot_file = 'map-{}-{}'.format(seed, density)
                    # ~ if not e.isfile(plot_file):
                        # ~ e.plot(filename = plot_file)
                    try:
                        e.run(relaxed=True, verbose=False)
                    except:
                        raise
                        print('exiting simulation... bye bye')
                    deployment.remove_end_devices()
    deployment.reset()


if __name__ == '__main__':
    lorawan_sim()
