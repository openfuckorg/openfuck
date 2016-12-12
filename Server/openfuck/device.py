"""
Handle all hardware communication.
"""

import asyncio
import attr
import logging
import serial
import serial.aio
import sys


__author__ = "riggs"


SWITCH = {'port': '/dev/ttyACM0', 'baudrate': 115200}
VALVES = {'port': '/dev/ttyACM1', 'baudrate': 115200}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr,
)
log = logging.getLogger('device')


@attr.s(frozen=True)
class Serial:
    reader = attr.ib()
    writer = attr.ib()

    @classmethod
    async def connect(cls, loop, port, baudrate):
        log.debug("connecting to {port} {baudrate}".format(port=port, baudrate=baudrate))
        return cls(*await serial.aio.open_serial_connection(loop=loop, port=port, baudrate=baudrate))


async def coro_factory(stroke, loop, stop_future, port, baudrate):
    connection = await Serial.connect(loop=loop, port=port, baudrate=baudrate)
    while not stop_future.done():
        # TODO: Logic

        pass
    else:
        connection.writer.close()


async def connect(stroke, loop, stop_future):
    loop.run_until_complete(coro_factory(stroke, loop, stop_future, **SWITCH))
    loop.run_until_complete(coro_factory(stroke, loop, stop_future, **VALVES))
