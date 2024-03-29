#!/usr/bin/env python3

DEFAULT = lambda: None

DEFAULT.RADIO = lambda: None
DEFAULT.RADIO.DIRECTION = lambda: None
DEFAULT.RADIO.DIRECTION.TX = 'TX'
DEFAULT.RADIO.DIRECTION.RX = 'RX'
DEFAULT.RADIO.DIRECTION.TXRX = 'TXRX'
DEFAULT.RADIO.STATE = lambda: None
DEFAULT.RADIO.STATE.SLEEP = 'SLEEP'
DEFAULT.RADIO.STATE.TRANSMITTING = 'TRANSMITTING'
DEFAULT.RADIO.STATE.LISTENING = 'LISTENING'
DEFAULT.RADIO.STATE.RECEIVING = 'RECEIVING'
DEFAULT.RADIO.STATE.COLLISION = 'COLLISION'

DEFAULT.DEVICE = lambda: None
DEFAULT.DEVICE.COMMON = lambda: None
DEFAULT.DEVICE.COMMON.channels = tuple(range(1,2))
DEFAULT.DEVICE.COMMON.coverage_range = 1
DEFAULT.DEVICE.OPTIONAL = lambda: None
DEFAULT.DEVICE.OPTIONAL.output_bufsize = 1
DEFAULT.DEVICE.OPTIONAL.input_bufsize = 0

DEFAULT.GATEWAY = lambda: None
DEFAULT.GATEWAY.duty_cycle = 100.0
DEFAULT.GATEWAY.channels = tuple(range(1,7))
DEFAULT.GATEWAY.output_bufsize = 4
DEFAULT.GATEWAY.input_bufsize = 5

DEFAULT.ENDDEVICE = lambda: None
DEFAULT.ENDDEVICE.channels = tuple(range(1,4))
DEFAULT.ENDDEVICE.interarrival_time = 200.0
DEFAULT.ENDDEVICE.time_tx_packet = 1.0
DEFAULT.ENDDEVICE.duty_cycle = 100.0
DEFAULT.ENDDEVICE.backlog_until_end_of_duty_cycle = False
DEFAULT.ENDDEVICE.output_bufsize = 2
DEFAULT.ENDDEVICE.input_bufsize = 3

DEFAULT.EDSTATE = lambda: None
DEFAULT.EDSTATE.IDLE = 'IDLE'
DEFAULT.EDSTATE.TRANSMITTING = 'TRANSMITTING'
DEFAULT.EDSTATE.DUTYCYCLE = 'DUTYCYCLE'

DEFAULT.GWSTATE = lambda: None
DEFAULT.GWSTATE.IDLE = 'IDLE'
DEFAULT.GWSTATE.RECEIVING = 'RECEIVING'
DEFAULT.GWSTATE.COLLISION = 'COLLISION'

DEFAULT.LORADEVICE_CLASS = lambda: None
DEFAULT.LORADEVICE_CLASS.A = 'CLASS_A'
DEFAULT.LORADEVICE_CLASS.B = 'CLASS_B'
DEFAULT.LORADEVICE_CLASS.C = 'CLASS_C'
DEFAULT.LORADEVICE_CLASS.S_SLOTTED_ALOHA = 'CLASS_S_SLOTTED_ALOHA'
DEFAULT.LORADEVICE_CLASS.S_SINGLE_GW_SCHEDULING = 'CLASS_S_SINGLE_GW_SCHEDULING'

DEFAULT.THEORETICAL_CLASS = lambda: None
DEFAULT.THEORETICAL_CLASS.PURE_ALOHA = 'THEORETICAL_PURE_ALOHA'
DEFAULT.THEORETICAL_CLASS.SLOTTED_ALOHA = 'THEORETICAL_SLOTTED_ALOHA'

DEFAULT.PACKET = lambda: None
DEFAULT.PACKET.GENERATED = 'GENERATED'
DEFAULT.PACKET.STARTTX = 'STARTTX'
DEFAULT.PACKET.STOPTX = 'STOPTX'
DEFAULT.PACKET.STARTRX = 'STARTRX'
DEFAULT.PACKET.STOPRX = 'STOPRX'
DEFAULT.PACKET.TORTX = 'TORTX'
DEFAULT.PACKET.CHANNEL = 'CHANNEL'
DEFAULT.PACKET.OUTCOME = 'OUTCOME'
DEFAULT.PACKET.TX = 'TX'
DEFAULT.PACKET.RX = 'RX'

DEFAULT.BUFFER = lambda: None
DEFAULT.BUFFER.SIZE = 1
DEFAULT.BUFFER.SELECTCONDITION = lambda x: True

DEFAULT.DEPLOYMENT = lambda: None
DEFAULT.DEPLOYMENT.HONEYCOMB = 'HONEYCOMB'
DEFAULT.DEPLOYMENT.SQUARE = 'SQUARE'
DEFAULT.DEPLOYMENT.POISSON = 'POISSON'
DEFAULT.DEPLOYMENT.GENERIC = 'GENERIC'
DEFAULT.DEPLOYMENT.SINGLE = 'SINGLE'
DEFAULT.DEPLOYMENT.INTRAGW_DISTANCE = 1
DEFAULT.DEPLOYMENT.COVERAGE_RANGE = 1
DEFAULT.DEPLOYMENT.HONEYCOMB_GW_PER_ROW = 10
DEFAULT.DEPLOYMENT.HONEYCOMB_ROWS = 12
DEFAULT.DEPLOYMENT.SQUARE_GW_PER_ROW = 10
DEFAULT.DEPLOYMENT.SQUARE_ROWS = 10
DEFAULT.DEPLOYMENT.POISSON_WIDTH = 10
DEFAULT.DEPLOYMENT.POISSON_HEIGHT = 10
DEFAULT.DEPLOYMENT.POISSON_GW_DENSITY = 1
DEFAULT.DEPLOYMENT.POISSON_ED_DENSITY = 10

DEFAULT.TIME_TX_PACKET_MAX      = 0.368896
DEFAULT.TIME_TX_PACKET_MIN      = 0.046336
DEFAULT.INTERARRIVAL_TIME_MIN   = 60
DEFAULT.INTERARRIVAL_TIME_MAX   = 600
DEFAULT.DURATION                = 60*60*1
DEFAULT.SIDE                    = 'SIDE'
DEFAULT.AREA                    = 'AREA'
DEFAULT.UNIONS                  = 'UNIONS'
DEFAULT.COEFFICIENTS            = 'COEFFICIENTS'
DEFAULT.SEPARATOR = '----------SEPARATOR----------'

DEFAULT.BEACON_PERIOD = 128
DEFAULT.BEACON_RESERVED = 2.120
DEFAULT.BEACON_WINDOW = 122.880
DEFAULT.BEACON_GUARD = 3
DEFAULT.PINGSLOT_SIZE = 0.030

DEFAULT.OUTPUT_FOLDER_NAME = 'lorawan-sim-outputs'
DEFAULT.ROOT_DIRECTORY = '.'
