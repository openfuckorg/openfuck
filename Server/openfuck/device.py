"""
Handle all hardware communication.
"""

import asyncio
import logging
import serial
import serial.aio
import sys

from collections.abc import Sequence


__author__ = "riggs"


SWITCH = ('/dev/ttyACM0', 115200)
VALVES = ('/dev/ttyACM1', 115200)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr,
)
log = logging.getLogger('main')

event_loop = asyncio.get_event_loop()


class Serial(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.log = logging.getLogger('Serial_{}'.format(self.transport))
        self.log.debug('connected')

    def data_received(self, data):
        self.log.debug('received {!r}'.format(data))
        # TODO: Handle message.

    def connection_lost(self, error):
        if error:
            self.log.error('ERROR: {}'.format(error))
            event_loop.stop()
        else:
            self.log.debug('connection closed')
        super().connection_lost(error)

    def write(self, data):
        if not isinstance(data, bytes):
            if isinstance(data, Sequence):
                data = bytes(data)
            elif isinstance(data, int):
                data = bytes((data,))
            else:
                raise TypeError("cannot convert to bytes: {}".format(data))
        self.log.debug("writing {}".format(data))
        self.transport.write(data)


switch_coro = serial.aio.create_serial_connection(event_loop, Serial, *SWITCH)
valves_coro = serial.aio.create_serial_connection(event_loop, Serial, *VALVES)
switch_transport, switch_protocol = event_loop.run_until_complete(switch_coro)
valves_transport, valves_protocol = event_loop.run_until_complete(valves_coro)
log.debug("starting {} {}".format(*SWITCH))
log.debug("starting {} {}".format(*VALVES))
