"""
Hardware drivers used by device.py
"""
import attr
import asyncio
# import serial
from .serial_asyncio import open_serial_connection

from .logger import logger

__author__ = "riggs"

SWITCH = {'url': 'hwgrep:///dev/ttyACM0', 'baudrate': 115200}
VALVES = {'url': 'hwgrep:///dev/ttyACM1', 'baudrate': 115200}

log = logger('driver')


@attr.s(frozen=True)
class Serial:
    reader = attr.ib()
    writer = attr.ib()

    @classmethod
    async def connect(cls, loop, url, baudrate):
        log.debug("connecting to {url} {baudrate} in {loop}".format(loop=loop, url=url, baudrate=baudrate))
        return cls(*await open_serial_connection(loop=loop, url=url, baudrate=baudrate))


class Driver:
    def __init__(self, loop):
        self.loop = loop
        self.connected = False
        self.switch = None
        self.valves = None
        self.last_stroke = None

    async def connect(self):
        self.switch = await Serial.connect(loop=self.loop, **SWITCH)
        self.valves = await Serial.connect(loop=self.loop, **VALVES)
        self.connected = True

    async def read(self):
        if not self.connected:
            await self.connect()
        result = await self.switch.reader.read(1)[0]
        if result in (255, 254):
            return True
        else:
            raise ValueError("unknown return value from hardware: {}".format(result))

    async def write(self, stroke):
        if not self.connected:
            await self.connect()
        position = bytes((int(stroke.position * 255),))
        if self.last_stroke:
            offset = 0 if self.last_stroke.position > stroke.position else 101
            speed = bytes((int(stroke.speed * 100 + offset),))
            self.valves.writer.write(speed)
            await self.valves.writer.drain()
        else:   # First time, no last position
            speed = bytes((int(stroke.speed * 100),))
            self.valves.writer.write(speed)
            await self.valves.writer.drain()
            speed = bytes((int(stroke.speed * 100 + 101),))
            self.valves.writer.write(speed)
            await self.valves.writer.drain()
        self.switch.writer.write(position)
        await self.switch.writer.drain()

    def close(self):
        self.switch.writer.close()
        self.valves.writer.close()


class Test_Driver:
    def __init__(self, loop):
        self.loop = loop
        self.connected = False
        self.log = logger(loop.__class__.__name__)

    async def connect(self):
        self.log.debug('connecting')
        await asyncio.sleep(0.01)
        self.connected = True

    async def read(self):
        if not self.connected:
            await self.connect()
        self.log.debug('reading')
        await asyncio.sleep(1)
        return True

    async def write(self, stroke):
        if not self.connected:
            await self.connect()
        self.log.debug('writing {}'.format(stroke))

    def close(self):
        self.log.debug('closed')
