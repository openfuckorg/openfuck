"""
Hardware drivers used by device.py
"""
import attr

from .device import Base_Driver
from .logger import logger
from serial_asyncio import open_serial_connection

__author__ = "riggs"

SWITCH = {'url': 'hwgrep:///dev/ttyACM0', 'baudrate': 115200}
VALVES = {'url': 'hwgrep:///dev/ttyACM1', 'baudrate': 115200}

log = logger('serial driver')


@attr.s(frozen=True)
class Serial:
    reader = attr.ib()
    writer = attr.ib()

    @classmethod
    async def connect(cls, loop, url, baudrate):
        log.debug("connecting to {url} {baudrate} in {loop}".format(loop=loop, url=url, baudrate=baudrate))
        return cls(*await open_serial_connection(loop=loop, url=url, baudrate=baudrate))


class Serial_Driver(Base_Driver):
    done_values = [254, 255]

    def __init__(self, loop):
        super().__init__(loop)
        self.switch = None
        self.valves = None
        self.last_stroke = None
        self.log = logger(self.__class__.__name__)

    async def _connect(self):
        self.switch = await Serial.connect(loop=self.loop, **SWITCH)
        self.valves = await Serial.connect(loop=self.loop, **VALVES)

    async def _read(self):
        result = (await self.switch.reader.read(1))[0]
        self.log.debug("read {}".format(result))
        if result in (255, 254):
            return result
        else:
            raise ValueError("unknown return value from hardware: {}".format(result))

    async def _write(self, stroke):
        position = bytes((int(stroke.position * 255),))
        if self.last_stroke:
            offset = 0 if self.last_stroke.position < stroke.position else 101
            speed = bytes((int(stroke.speed * 100 + offset),))
            self.log.debug("writing speed {}".format(speed))
            self.valves.writer.write(speed)
            await self.valves.writer.drain()
        else:  # First time, no last position
            speed = bytes((int(stroke.speed * 100),))
            self.log.debug("writing speed {}".format(speed))
            self.valves.writer.write(speed)
            await self.valves.writer.drain()
            speed = bytes((int(stroke.speed * 100 + 101),))
            self.log.debug("writing speed {}".format(speed))
            self.valves.writer.write(speed)
            await self.valves.writer.drain()
        self.log.debug("writing position {}".format(position))
        self.switch.writer.write(position)
        await self.switch.writer.drain()
        self.last_stroke = stroke

    def _close(self):
        self.log.debug('closing')
        self.switch.writer.close()
        self.valves.writer.close()
