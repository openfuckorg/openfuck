"""
Hardware drivers used by device.py
"""
import asyncio

import attr

from .logger import logger
from .serial_asyncio import open_serial_connection

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
        else:  # First time, no last position
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
        self.connected = asyncio.Event(loop=loop)
        self._connecting = asyncio.Event(loop=loop)
        self.log = logger("Hardware Driver")
        self.moving = asyncio.Event(loop=loop)

    async def connect(self):
        if not self.connected.is_set() and \
                not self._connecting.is_set():
            self._connecting.set()
            self.log.debug('connecting')
            await asyncio.sleep(0.1)
            self.connected.set()
            self.log.debug('connected')
        else:
            self.log.debug('waiting for connection')
            await self.connected.wait()
            self.log.debug('connection ready')

    async def read(self):
        self.log.debug('start reading')
        if not self.connected.is_set():
            await self.connect()
        await self.moving.wait()
        await asyncio.sleep(1)
        self.moving.clear()
        self.log.debug('stopped "moving"')
        self.log.debug('finished reading')
        return True

    async def write(self, stroke):
        self.log.debug('start writing {}'.format(stroke))
        if not self.connected.is_set():
            await self.connect()
        self.log.debug('finished writing')
        await asyncio.sleep(0.01)
        self.moving.set()
        self.log.debug('started "moving"')

    def close(self):
        self.connected.clear()
        self._connecting.clear()
        self.log.debug('closed')
