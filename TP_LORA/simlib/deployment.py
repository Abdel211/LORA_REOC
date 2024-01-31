#!/usr/bin/env python3

from __future__ import division
import math
import matplotlib.pyplot as plt
import numpy

from simlib.borg import *
from simlib.monitor import *
from simlib.eventscheduler import *
from simlib.lora.loraenddevice import LoRaEndDevice
from simlib.lora.loragateway import LoRaGateway
from simlib.defaults import *
from simlib.randomness import *


class Deployment(Borg):
    ''' Public Borg methods to be defined in subclasses '''

    def init(self, width=None, height=None, gateways=None, end_devices=None, delete=False, check_coverage=False,
             **kwargs):
        if self.master_exists() and not self.is_master():
            raise AttributeError('a bug is present, this must never happen')
        if None in [width, height]:
            if self.master_exists():
                self.reset()
                raise ValueError(
                    'master cannot be set without proper values for width and/or height and/or distance unit')
            if width != height:
                raise ValueError(
                    'width and height must be configured to have simultaneously their own value or to be both set to None')
            if gateways or end_devices:
                raise ValueError(
                    'gateways and end devices can be added/deleted after that width and height have been specified')
            if kwargs:
                raise ValueError('further arguments can be specified when also defining width and height')
            return
        self.set_master_permitting_update()
        self.__dimensions = (width, height)
        self.__gateways = dict()
        self.__end_devices = dict()
        self.__init_common()
        self.__set_common(**kwargs)
        self.init_update(gateways=gateways, end_devices=end_devices, delete=delete, check_coverage=check_coverage)
        self.monitor = Monitor()
        self.event_scheduler = EventScheduler()
        self.device_infrastructure = self.__device_infrastructure
        self.gateway_infrastructure = self.__gateway_infrastructure
        self.end_device_infrastructure = self.__end_device_infrastructure
        self.single_gateway_infrastructure = self.__single_gateway_infrastructure
        self.honeycomb_gateway_infrastructure = self.__honeycomb_gateway_infrastructure
        self.square_gateway_infrastructure = self.__square_gateway_infrastructure
        self.poisson_gateway_infrastructure = self.__poisson_gateway_infrastructure
        self.poisson_end_device_infrastructure = self.__poisson_end_device_infrastructure

    def init_update(self,
                    gateways=None,
                    end_devices=None,
                    delete=False,
                    check_coverage=False
                    ):
        is_gateway = lambda device: isinstance(device, LoRaGateway)
        is_end_device = lambda device: isinstance(device, LoRaEndDevice)
        is_connected = lambda device: bool(device.connections)
        is_disconnected = lambda device: not bool(device.connections)
        gateways = set(gateways) if gateways != None else set()
        assert all(map(is_gateway, gateways))
        end_devices = set(end_devices) if end_devices != None else set()
        assert all(map(is_end_device, end_devices))
        if not delete:
            all_end_devices = set(self.__end_devices.values())
            all_end_devices |= end_devices
            all_gateways = set(self.__gateways.values())
            all_gateways |= gateways
            for device in gateways | end_devices:
                if not self.__is_device_admittable(device):
                    raise ValueError('{} {} is not admittable'.format(
                        device.__class__.__name__,
                        device.get_attributes().id_device))
                if is_gateway(device):
                    neighbors = all_end_devices
                else:
                    neighbors = all_gateways
                for neighbor in neighbors:
                    device.connect(neighbor)
            all_end_devices = set(self.__end_devices.values())
            all_end_devices |= end_devices
            all_gateways = set(self.__gateways.values())
            all_gateways |= gateways
            condition = not check_coverage
            condition |= all(map(is_connected, gateways | end_devices))
            condition |= (bool(all_end_devices) != bool(all_gateways))
            if condition:
                for gateway in gateways:
                    id_device = gateway.get_attributes().id_device
                    self.__gateways[id_device] = gateway
                for end_device in end_devices:
                    id_device = end_device.get_attributes().id_device
                    self.__end_devices[id_device] = end_device
            elif bool(end_devices) != bool(gateways):
                for gateway in filter(is_connected, gateways):
                    id_device = gateway.get_attributes().id_device
                    self.__gateways[id_device] = gateway
                for end_device in filter(is_connected, end_devices):
                    id_device = end_device.get_attributes().id_device
                    self.__end_devices[id_device] = end_device
            else:
                for device in gateways | end_devices:
                    device.disconnect()
            return
        for device in gateways | end_devices:
            device.disconnect()
        old_gateways = set(self.__gateways.values())
        old_end_devices = set(self.__end_devices.values())
        left_gateways = old_gateways - gateways
        left_end_devices = old_end_devices - end_devices
        condition = check_coverage
        condition |= bool(left_end_devices) == bool(left_gateways)
        if condition:
            gateways.update(filter(is_disconnected, old_gateways))
            end_devices.update(filter(is_disconnected, old_end_devices))
        for device in gateways | end_devices:
            id_device = device.get_attributes().id_device
            if is_gateway(device):
                self.__gateways.pop(id_device)
            else:
                self.__end_devices.pop(id_device)
        self.__init_common()

    ''' Public factory methods '''

    @classmethod
    def device_infrastructure(cls, grid, device_type, **kwargs):
        if device_type not in {LoRaEndDevice, LoRaGateway}:
            raise AttributeError('unrecognized device type')
        common = set(DEFAULT.DEVICE.COMMON.__dict__)
        default_device_dict = DEFAULT.GATEWAY.__dict__ if device_type == LoRaGateway else DEFAULT.ENDDEVICE.__dict__
        common_device = (set(default_device_dict) | set(DEFAULT.DEVICE.OPTIONAL.__dict__)) - common
        common_gateway, common_end_device = (common_device, None) if device_type == LoRaGateway else (
            None, common_device)
        device_kwargs = dict(DEFAULT.DEVICE.OPTIONAL.__dict__)
        device_kwargs.update(DEFAULT.DEVICE.COMMON.__dict__)
        device_kwargs.update({key: default_device_dict[key] for key in common_device if key in default_device_dict})
        device_kwargs.update({key: kwargs[key] for key in set(kwargs) & (common_device | common)})
        devices = [device_type(i, *item, **device_kwargs) for i, item in enumerate(grid)]
        gateways, end_devices = (devices, None) if device_type == LoRaGateway else (None, devices)
        return cls(gateways=gateways, end_devices=end_devices, common=common, common_gateway=common_gateway,
                   common_end_device=common_end_device, **kwargs)

    @classmethod
    def gateway_infrastructure(cls, grid, **kwargs):
        return cls.device_infrastructure(grid=grid, device_type=LoRaGateway, **kwargs)

    @classmethod
    def end_device_infrastructure(cls, grid, **kwargs):
        return cls.device_infrastructure(grid=grid, device_type=LoRaEndDevice, **kwargs)

    @classmethod
    def single_gateway_infrastructure(cls, width=None, height=None, coverage_range=DEFAULT.DEPLOYMENT.COVERAGE_RANGE,
                                      **kwargs):
        if width is not None and height is not None:
            grid = [(width / 2, height / 2)]
        elif width is None and height is None:
            grid = [(coverage_range, coverage_range)]
            width = 2 * coverage_range
            height = 2 * coverage_range
        else:
            raise ValueError('width and height must be both None or both set to any values')
        gateway_deployment = {'type_of_grid': DEFAULT.DEPLOYMENT.SINGLE}
        return cls.gateway_infrastructure(grid=grid, width=width, height=height, coverage_range=coverage_range,
                                          gateway_deployment=gateway_deployment, **kwargs)

    @classmethod
    def __regular_gateway_infrastructure(cls, gateway_deployment, width=None, height=None, **kwargs):
        if width is not None or height is not None:
            raise ValueError('width and height cannot be defined')
        grid = Deployment.__create_regular_grid(**gateway_deployment)
        width, _ = max(grid, key=lambda x: x[0])
        _, height = max(grid, key=lambda x: x[1])
        return cls.gateway_infrastructure(grid=grid, width=width, height=height, gateway_deployment=gateway_deployment,
                                          **kwargs)

    @classmethod
    def honeycomb_gateway_infrastructure(cls, gateways_per_row=DEFAULT.DEPLOYMENT.HONEYCOMB_GW_PER_ROW,
                                         rows=DEFAULT.DEPLOYMENT.HONEYCOMB_ROWS,
                                         intragw_distance=DEFAULT.DEPLOYMENT.INTRAGW_DISTANCE, **kwargs):
        gateway_deployment = {'type_of_grid': DEFAULT.DEPLOYMENT.HONEYCOMB, 'gateways_per_row': gateways_per_row,
                              'rows': rows, 'intragw_distance': intragw_distance}
        return cls.__regular_gateway_infrastructure(gateway_deployment, **kwargs)

    @classmethod
    def square_gateway_infrastructure(cls, gateways_per_row=DEFAULT.DEPLOYMENT.SQUARE_GW_PER_ROW,
                                      rows=DEFAULT.DEPLOYMENT.SQUARE_ROWS,
                                      intragw_distance=DEFAULT.DEPLOYMENT.INTRAGW_DISTANCE, **kwargs):
        gateway_deployment = {'type_of_grid': DEFAULT.DEPLOYMENT.SQUARE, 'gateways_per_row': gateways_per_row,
                              'rows': rows, 'intragw_distance': intragw_distance}
        return cls.__regular_gateway_infrastructure(gateway_deployment, **kwargs)

    @classmethod
    def poisson_gateway_infrastructure(cls, width=DEFAULT.DEPLOYMENT.POISSON_WIDTH,
                                       height=DEFAULT.DEPLOYMENT.POISSON_HEIGHT,
                                       density=DEFAULT.DEPLOYMENT.POISSON_GW_DENSITY, **kwargs):
        grid = Deployment.__create_poisson_grid(width, height, density)
        gateway_deployment = {'type_of_grid': DEFAULT.DEPLOYMENT.POISSON, 'density': density}
        return cls.gateway_infrastructure(grid=grid, width=width, height=height, gateway_deployment=gateway_deployment,
                                          **kwargs)

    @classmethod
    def poisson_end_device_infrastructure(cls, width=DEFAULT.DEPLOYMENT.POISSON_WIDTH,
                                          height=DEFAULT.DEPLOYMENT.POISSON_HEIGHT,
                                          density=DEFAULT.DEPLOYMENT.POISSON_ED_DENSITY, **kwargs):
        grid = Deployment.__create_poisson_grid(width, height, density)
        end_device_deployment = {'type_of_grid': DEFAULT.DEPLOYMENT.POISSON, 'density': density}
        return cls.end_device_infrastructure(grid=grid, width=width, height=height,
                                             end_device_deployment=end_device_deployment, **kwargs)

    ''' Public methods '''

    def reset_gateways(self, **kwargs):
        for gateway in self.__gateways.values():
            gateway.reset(**kwargs)
        self.__reset_common_gateway(**kwargs)
        for gateway in self.__gateways.values():
            if not self.__is_device_admittable(gateway):
                raise ValueError('gateway {} is not admittable anymore'.format(gateway.id_device))

    def reset_end_devices(self, **kwargs):
        for end_device in self.__end_devices.values():
            end_device.reset(**kwargs)
        self.__reset_common_end_device(**kwargs)
        for end_device in self.__end_devices.values():
            if not self.__is_device_admittable(end_device):
                raise ValueError('end device {} is not admittable anymore'.format(end_device.id_device))

    def remove_end_devices(self):
        self.init_update(end_devices=list(self.__end_devices.values()), delete=True)

    def remove_gateways(self):
        self.init_update(gateways=list(self.__gateways.values()), delete=True)

    def get_dimensions(self):
        if not self.master_exists():
            raise AttributeError('dimensions are not set')
        return self.__dimensions

    def plot(self, plot_connections=False, plot_evaluation_area=False, filename='plot', png=True, eps=False):
        if not self.master_exists():
            raise AttributeError('dimensions are not set')
        xx_bs = [self.__gateways[i].get_attributes().x for i in sorted(self.__gateways.keys())]
        yy_bs = [self.__gateways[i].get_attributes().y for i in sorted(self.__gateways.keys())]
        xx_ed = [self.__end_devices[i].get_attributes().x for i in sorted(self.__end_devices.keys())]
        yy_ed = [self.__end_devices[i].get_attributes().y for i in sorted(self.__end_devices.keys())]
        plt.figure(figsize=(6, 6))
        if plot_evaluation_area:
            if self.__gateway_deployment.type_of_grid == DEFAULT.DEPLOYMENT.SINGLE:
                gateway = list(self.__gateways.values())[0]
                circle = plt.Circle((gateway.get_attributes().x, gateway.get_attributes().y),
                                    gateway.get_attributes().coverage_range, color='black', linestyle='--', fill=False)
                fig = plt.gcf()
                ax = fig.gca()
                ax.add_artist(circle)
            elif hasattr(self.__common, 'coverage_range') and self.__dimensions[
                0] > 4 * self.__common.coverage_range and self.__dimensions[1] > 4 * self.__common.coverage_range:
                coverage_range = self.__common.coverage_range
                plt.plot([2 * coverage_range, self.__dimensions[0] - 2 * coverage_range,
                          self.__dimensions[0] - 2 * coverage_range, 2 * coverage_range, 2 * coverage_range],
                         [2 * coverage_range, 2 * coverage_range, self.__dimensions[1] - 2 * coverage_range,
                          self.__dimensions[1] - 2 * coverage_range, 2 * coverage_range], linewidth=3, color='black',
                         zorder=0)
        if plot_connections:
            for ed in self.__end_devices.values():
                for gw in ed.connections:
                    if ed in gw.connections:
                        plt.plot([ed.get_attributes().x, gw.get_attributes().x],
                                 [ed.get_attributes().y, gw.get_attributes().y], color='0.2', linestyle='dotted',
                                 zorder=1)
        plt.scatter(xx_bs, yy_bs, marker='D', s=30, c='k', zorder=3, label='Gateway')
        plt.scatter(xx_ed, yy_ed, c='w', edgecolors='k', zorder=2, label='End-device')
        plt.axis('scaled')
        plt.legend(loc='center', bbox_to_anchor=(0.9, 0.97), scatterpoints=1)
        plt.xlim(0, self.__dimensions[0])
        plt.ylim(0, self.__dimensions[1])
        if png:
            plt.savefig('{}.png'.format(filename), dpi=100)
        if eps:
            plt.savefig('{}.eps'.format(filename), dpi=100)
        plt.close()

    def prepare(self):

        def create_string(attr, label=''):
            var = ''
            for key, value in sorted(attr.__dict__.items()):
                var += '{} {} '.format(key, value)
            if var:
                var = ' '.join([label, var])
            return var

        if not self.master_exists():
            raise AttributeError('the deployment is not correctly initializd')
        dimensions = 'AREA width {} height {} '.format(*self.__dimensions)
        gateway_deployment = create_string(self.__gateway_deployment, label='GWDEP')
        end_device_deployment = create_string(self.__end_device_deployment, label='EDDEP')
        common = create_string(self.__common, label='COM')
        common_gateway = create_string(self.__common_gateway, label='GWCOM')
        common_end_device = create_string(self.__common_end_device, label='EDCOM')
        string_deployment = ''.join(
            [dimensions, gateway_deployment, end_device_deployment, common, common_gateway, common_end_device]).strip()
        string_deployment_specific = ''
        for id_device in sorted(self.__end_devices.keys()):
            string_deployment_specific += 'ED {} {} {} '.format(id_device,
                                                                self.__end_devices[id_device].get_attributes().x,
                                                                self.__end_devices[id_device].get_attributes().y)
        for id_device in sorted(self.__gateways.keys()):
            string_deployment_specific += 'GW {} {} {} '.format(id_device,
                                                                self.__gateways[id_device].get_attributes().x,
                                                                self.__gateways[id_device].get_attributes().y)
        self.monitor.logline(string_deployment, True, True)
        self.monitor.logline(string_deployment_specific, True, False)

    def start(self):
        for id_device in sorted(self.__end_devices.keys()):
            self.__end_devices[id_device].start()
        for id_device in sorted(self.__gateways.keys()):
            self.__gateways[id_device].start()

    def save_stats(self, relaxed=False):  # to be updated in a more scalable manner
        if not hasattr(self.__common_end_device, 'time_tx_packet'):
            raise AttributeError('this method cannot be called if time_tx_packet is not unique')
        if not hasattr(self.__common, 'coverage_range') and not relaxed:
            raise AttributeError('this method cannot be called if coverage range is not unique')

        margin = 2 * self.__common.coverage_range if not relaxed and self.__gateway_deployment.type_of_grid != DEFAULT.DEPLOYMENT.SINGLE else 0
        g = 0
        t = 0
        checked_rx = 3
        rx = dict((i, 0) for i in range(1, 1 + checked_rx))
        d = dict((i, []) for i in range(1, 1 + checked_rx))
        for id_device in sorted(self.__end_devices.keys()):
            end_device = self.__end_devices[id_device]
            stats = end_device.statistics
            log_message = '#E{} GEN {} TX {} '.format(id_device, stats['GEN'], stats['TX'])
            log_message += ''.join(
                ['RX{} {} '.format(i, stats['RX'][i] if i in stats['RX'] else 0.0) for i in range(1, 1 + checked_rx)])
            for i in range(1, 1 + checked_rx):
                log_message += 'D{} '.format(i)
                d_array = stats['D'][i][:-1] if i in stats['D'] else []
                log_message += '{} '.format(numpy.mean(d_array) if d_array else numpy.nan)
                log_message += '{} '.format(numpy.mean(numpy.array(d_array) ** 2) if d_array else numpy.nan)
                log_message += '{} '.format(len(stats['D'][i][:-1]) if i in stats['D'] else 0)
            log_message = log_message[:-1]
            self.monitor.logline(log_message, True, False)
            if (
                    (self.__dimensions[0] > 2 * margin) and (self.__dimensions[1] > 2 * margin)
                    and
                    (end_device.get_attributes().x >= margin) and (
                    end_device.get_attributes().x <= self.__dimensions[0] - margin)
                    and
                    (end_device.get_attributes().y >= margin) and (
                    end_device.get_attributes().y <= self.__dimensions[1] - margin)
            ):
                g += stats['GEN']
                t += stats['TX']
                for i in range(1, 1 + checked_rx):
                    rx[i] += stats['RX'][i] if i in stats['RX'] else 0
                    d[i] += stats['D'][i][:-1] if i in stats['D'] else []

        log_message = '#TOT GEN {} TX {} '.format(g, t)
        log_message += ''.join(['RX{} {} '.format(i, rx[i] if i in rx else 0.0) for i in range(1, 1 + checked_rx)])
        area = (self.__dimensions[0] - 2 * margin) * (self.__dimensions[
                                                          1] - 2 * margin) if self.__gateway_deployment.type_of_grid != DEFAULT.DEPLOYMENT.SINGLE else math.pi
        estimated_throughput = lambda x: self.__common_end_device.time_tx_packet * math.pi * x / (
                self.event_scheduler.get_duration() * area)
        log_message += ''.join(
            ['T{} {} '.format(i, estimated_throughput(rx[i]) if i in rx else 0.0) for i in range(1, 1 + checked_rx)])
        for i in range(1, 1 + checked_rx):
            log_message += 'D{} '.format(i)
            log_message += '{} '.format(numpy.mean(d[i]) if (i in d and d[i]) else numpy.nan)
            log_message += '{} '.format(numpy.mean(numpy.array(d[i]) ** 2) if (i in d and d[i]) else numpy.nan)
            log_message += '{} '.format(len(d[i]) if i in d else 0)
        log_message = log_message[:-1]
        self.monitor.logline(log_message, True, True)

    def get_gateways(self):  # do not use until it is modified to hinder modification of gateways
        return self.__gateways

    def get_lengths(self):

        if not [device for device in self.__gateways.values()] + [device for device in self.__end_devices.values()]:
            control = False
        elif [device for device in self.__gateways.values() if not device.connections] + [device for device in
                                                                                          self.__end_devices.values() if
                                                                                          not device.connections]:
            control = False
        else:
            control = True

        return len(self.__gateways), len(self.__end_devices), control

    ''' Private factory methods (they modify existent instance)'''

    def __device_infrastructure(self, grid, device_type, check_coverage=True, **kwargs):
        if not self.is_master():
            raise AttributeError('modification are authorized only for the master')
        if device_type not in {LoRaEndDevice, LoRaGateway}:
            raise AttributeError('unrecognized device type')
        if device_type == LoRaEndDevice and self.__end_devices:
            raise AttributeError('end devices infrastructure already set')
        elif device_type == LoRaGateway and self.__gateways:
            raise AttributeError('gateways infrastructure already set')
        if (self.__gateways or self.__end_devices) and set(self.__common.__dict__.keys()) != set(
                DEFAULT.DEVICE.COMMON.__dict__.keys()):
            raise AttributeError('this method cannot be used if coverage range and/or channels are not common')
        common = set(DEFAULT.DEVICE.COMMON.__dict__)
        default_device_dict = DEFAULT.GATEWAY.__dict__ if device_type == LoRaGateway else DEFAULT.ENDDEVICE.__dict__
        common_device = (set(default_device_dict) | set(DEFAULT.DEVICE.OPTIONAL.__dict__)) - common
        common_gateway, common_end_device = (common_device, None) if device_type == LoRaGateway else (
            None, common_device)
        self.__set_common(common=common, common_gateway=common_gateway, common_end_device=common_end_device, **kwargs)
        device_kwargs = dict(DEFAULT.DEVICE.OPTIONAL.__dict__)
        device_kwargs.update(DEFAULT.DEVICE.COMMON.__dict__)
        device_kwargs.update({key: default_device_dict[key] for key in common_device if key in default_device_dict})
        device_kwargs.update(dict(self.__common.__dict__, **(
            self.__common_gateway.__dict__ if device_type == LoRaGateway else self.__common_end_device.__dict__)))
        devices = [device_type(i, *item, **device_kwargs) for i, item in enumerate(grid)]
        gateways, end_devices = (devices, None) if device_type == LoRaGateway else (None, devices)
        self.init_update(gateways=gateways, end_devices=end_devices, check_coverage=check_coverage)

    def __gateway_infrastructure(self, grid, **kwargs):
        self.__device_infrastructure(grid, LoRaGateway, **kwargs)

    def __end_device_infrastructure(self, grid, **kwargs):
        self.__device_infrastructure(grid, LoRaEndDevice, **kwargs)

    def __single_gateway_infrastructure(self, **kwargs):
        grid = [(self.__dimensions[0] / 2, self.__dimensions[1] / 2)]
        gateway_deployment = {'type_of_grid': DEFAULT.DEPLOYMENT.SINGLE}
        self.__gateway_infrastructure(grid=grid, gateway_deployment=gateway_deployment, **kwargs)

    def __honeycomb_gateway_infrastructure(self, intragw_distance=DEFAULT.DEPLOYMENT.INTRAGW_DISTANCE, **kwargs):
        gateways_per_row = int(self.__dimensions[0] / intragw_distance)
        rows = int(self.__dimensions[1] / (intragw_distance * math.sqrt(3) / 2))
        gateway_deployment = {'type_of_grid': DEFAULT.DEPLOYMENT.HONEYCOMB, 'gateways_per_row': gateways_per_row,
                              'rows': rows, 'intragw_distance': intragw_distance}
        grid = Deployment.__create_regular_grid(**gateway_deployment)
        self.__gateway_infrastructure(grid=grid, gateway_deployment=gateway_deployment, **kwargs)

    def __square_gateway_infrastructure(self, intragw_distance=DEFAULT.DEPLOYMENT.INTRAGW_DISTANCE, **kwargs):
        gateways_per_row = int(self.__dimensions[0] / intragw_distance)
        rows = int(self.__dimensions[1] / intragw_distance)
        gateway_deployment = {'type_of_grid': DEFAULT.DEPLOYMENT.SQUARE, 'gateways_per_row': gateways_per_row,
                              'rows': rows, 'intragw_distance': intragw_distance}
        grid = Deployment.__create_regular_grid(**gateway_deployment)
        self.__gateway_infrastructure(grid=grid, gateway_deployment=gateway_deployment, **kwargs)

    def __poisson_gateway_infrastructure(self, density=DEFAULT.DEPLOYMENT.POISSON_GW_DENSITY, **kwargs):
        grid = Deployment.__create_poisson_grid(self.__dimensions[0], self.__dimensions[1], density)
        gateway_deployment = {'type_of_grid': DEFAULT.DEPLOYMENT.POISSON, 'density': density}
        self.__gateway_infrastructure(grid=grid, gateway_deployment=gateway_deployment, **kwargs)

    def __poisson_end_device_infrastructure(self, density=DEFAULT.DEPLOYMENT.POISSON_ED_DENSITY, **kwargs):
        grid = Deployment.__create_poisson_grid(self.__dimensions[0], self.__dimensions[1], density)
        end_device_deployment = {'type_of_grid': DEFAULT.DEPLOYMENT.POISSON, 'density': density}
        self.__end_device_infrastructure(grid=grid, end_device_deployment=end_device_deployment, **kwargs)

    ''' Private helper methods'''

    def __set_common(self, common=None, common_gateway=None, common_end_device=None, gateway_deployment=None,
                     end_device_deployment=None, **kwargs):
        common = common if isinstance(common, set) else set()
        common_gateway = common_gateway if isinstance(common_gateway, set) else set()
        common_end_device = common_end_device if isinstance(common_end_device, set) else set()
        if common & common_gateway:
            raise ValueError('not admittable common gateway')
        if common & common_end_device:
            raise ValueError('not admittable common end device')
        common -= set(self.__common.__dict__)
        self.__common.__dict__.update(
            {key: DEFAULT.DEVICE.COMMON.__dict__[key] for key in common & set(DEFAULT.DEVICE.COMMON.__dict__)})
        self.__common.__dict__.update({key: kwargs[key] for key in common & set(kwargs)})
        common_gateway = common_gateway - set(self.__common.__dict__) - set(self.__common_gateway.__dict__)
        self.__common_gateway.__dict__.update({key: DEFAULT.DEVICE.OPTIONAL.__dict__[key] for key in
                                               common_gateway & set(DEFAULT.DEVICE.OPTIONAL.__dict__)})
        self.__common_gateway.__dict__.update(
            {key: DEFAULT.GATEWAY.__dict__[key] for key in common_gateway & set(DEFAULT.GATEWAY.__dict__)})
        self.__common_gateway.__dict__.update({key: kwargs[key] for key in common_gateway & set(kwargs)})
        common_end_device = common_end_device - set(self.__common.__dict__) - set(self.__common_end_device.__dict__)
        self.__common_end_device.__dict__.update({key: DEFAULT.DEVICE.OPTIONAL.__dict__[key] for key in
                                                  common_end_device & set(DEFAULT.DEVICE.OPTIONAL.__dict__)})
        self.__common_end_device.__dict__.update(
            {key: DEFAULT.ENDDEVICE.__dict__[key] for key in common_end_device & set(DEFAULT.ENDDEVICE.__dict__)})
        self.__common_end_device.__dict__.update({key: kwargs[key] for key in common_end_device & set(kwargs)})
        self.__gateway_deployment.__dict__ = self.__gateway_deployment.__dict__ if gateway_deployment == None else gateway_deployment
        self.__end_device_deployment.__dict__ = self.__end_device_deployment.__dict__ if end_device_deployment == None else end_device_deployment

    def __init_common(self):
        if not self.__gateways:
            self.__common_gateway = lambda: None
            self.__gateway_deployment = lambda: None
            self.__gateway_deployment.type_of_grid = DEFAULT.DEPLOYMENT.GENERIC
        if not self.__end_devices:
            self.__common_end_device = lambda: None
            self.__end_device_deployment = lambda: None
            self.__end_device_deployment.type_of_grid = DEFAULT.DEPLOYMENT.GENERIC
        if not self.__gateways and not self.__end_devices:
            self.__common = lambda: None

    def __is_device_admittable(self, device):
        list_common = list(self.__common.__dict__.items())
        list_common += list(self.__common_gateway.__dict__.items()) if isinstance(device, LoRaGateway) else list(
            self.__common_end_device.__dict__.items())
        device_attributes = device.get_attributes()
        for key, value in list_common:
            if key in device_attributes.__dict__ and getattr(device_attributes, key) != value:
                return False
        return True

    def __reset_common_gateway(self, **kwargs):
        self.__common_gateway.__dict__.update(
            {key: kwargs[key] for key in set(self.__common_gateway.__dict__) & set(kwargs)})
        if not set(kwargs.keys()) & set(self.__common.__dict__.keys()):
            return
        if self.__end_devices:
            raise AttributeError('this method cannot be used to change common attributes if end devices are present')
        self.__common.__dict__.update({key: kwargs[key] for key in set(self.__common.__dict__) & set(kwargs)})

    def __reset_common_end_device(self, **kwargs):
        self.__common_end_device.__dict__.update(
            {key: kwargs[key] for key in set(self.__common_end_device.__dict__) & set(kwargs)})
        if not set(kwargs.keys()) & set(self.__common.__dict__.keys()):
            return
        if self.__gateways:
            raise AttributeError('this method cannot be used to change common attributes if gateways are present')
        self.__common.__dict__.update({key: kwargs[key] for key in set(self.__common.__dict__) & set(kwargs)})

    ''' Private helper static methods'''

    @staticmethod
    def __create_regular_grid(gateways_per_row, rows, intragw_distance, type_of_grid):
        if not isinstance(gateways_per_row, int):
            raise TypeError('the number of gateways per row must be an integer')
        if not isinstance(rows, int):
            raise TypeError('the number of rows must be an integer')
        if type_of_grid == DEFAULT.DEPLOYMENT.HONEYCOMB:
            grid = [(intragw_distance * (n + 0.5 * (row % 2)), intragw_distance * row * math.sqrt(3) / 2) for row in
                    range(rows + 1) for n in range(gateways_per_row + 1 - row % 2)]
        elif type_of_grid == DEFAULT.DEPLOYMENT.SQUARE:
            grid = [(intragw_distance * n, intragw_distance * row) for n in range(gateways_per_row + 1) for row in
                    range(rows + 1)]
        else:
            raise ValueError('unrecognized type of grid')
        return grid

    @staticmethod
    def __create_poisson_grid(width, height, density):
        if not width or not height:
            raise ValueError('width and height cannot be set to be null')
        predefined_numpy_random = Randomness().get_predefined_numpy_random()
        predefined_random = Randomness().get_predefined_random()
        number_of_devices = predefined_numpy_random.poisson(width * height * density)
        devices_grid = [(predefined_random.random() * width, predefined_random.random() * height) for i in
                        range(number_of_devices)]
        return devices_grid
