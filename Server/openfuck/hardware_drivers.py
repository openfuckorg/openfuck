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


class Base_Driver:

    done_values = []

    def __init__(self, loop):
        self.loop = loop
        self.connected = asyncio.Event(loop=loop)
        self._connecting = asyncio.Event(loop=loop)
        self.log = logger(self.__class__.__name__)

    async def connect(self):
        """
        Safely connect to device, ensuring only one connection.
        """
        if not self.connected.is_set() and \
                not self._connecting.is_set():
            self._connecting.set()
            self.log.debug('connecting')
            await self._connect()
            self.connected.set()
            self.log.debug('connected')
        else:
            self.log.debug('waiting for connection')
            await self.connected.wait()
            self.log.debug('connection ready')

    async def read(self):
        """
        Connect, if necessary, and read from device. _read must be supplied by subclass.
        """
        if not self.connected:
            self.log.debug('read connecting')
            await self.connect()
        self.log.debug('reading')
        return await self._read()

    async def stroke_finished(self):
        """
        Wait until device sends 'done moving' value, then return True, discarding any other values read.
        """
        value = await self.read()
        if value in self.done_values:
            return True
        else:
            return await self.stroke_finished()

    async def write(self, stroke):
        self.log.debug('start writing {}'.format(stroke))
        if not self.connected.is_set():
            await self.connect()
        await self._write(stroke)
        self.log.debug('finished writing')

    def close(self):
        self.connected.clear()
        self._connecting.clear()
        self._close()
        self.log.debug('closed')

    async def _connect(self):
        raise NotImplementedError

    async def _read(self):
        raise NotImplementedError

    async def _write(self, stroke):
        raise NotImplementedError

    async def _close(self):
        raise NotImplementedError


class Dev_Driver(Base_Driver):

    done_values = [254, 255]

    def __init__(self, loop):
        super().__init__(loop)
        self.switch = None
        self.valves = None
        self.last_stroke = None

    async def _connect(self):
        self.switch = await Serial.connect(loop=self.loop, **SWITCH)
        self.valves = await Serial.connect(loop=self.loop, **VALVES)

    async def _read(self):
        result = await self.switch.reader.read(1)[0]
        if result in (255, 254):
            return result
        else:
            raise ValueError("unknown return value from hardware: {}".format(result))

    async def _write(self, stroke):
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

    def _close(self):
        self.switch.writer.close()
        self.valves.writer.close()


class Test_Driver(Base_Driver):

    done_values = [True]

    def __init__(self, loop):
        super().__init__(loop)
        self.moving = asyncio.Event(loop=loop)

    async def _connect(self):
        await asyncio.sleep(0.1)

    async def _read(self):
        await self.moving.wait()
        await asyncio.sleep(1)
        self.moving.clear()
        self.log.debug('stopped "moving"')
        return True

    async def _write(self, stroke):
        await asyncio.sleep(0.01)
        self.moving.set()
        self.log.debug('started "moving"')

    def _close(self):
        pass
