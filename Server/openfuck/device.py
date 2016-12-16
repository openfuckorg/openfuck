"""
Simple API to handle all hardware communication.
"""

import asyncio

from .logger import logger

__author__ = "riggs"


async def connect(Driver, current_pattern, event_loop):

    log = logger('device communication')

    driver = Driver(event_loop)
    await driver.connect()

    async def loop():
        try:
            async for stroke in current_pattern:
                log.debug("writing {}".format(stroke))
                await driver.write(stroke)
                log.debug("waiting for stroke to finish")
                await driver.stroke_finished()
        finally:
            driver.close()

    event_loop.create_task(loop())


class Base_Driver:
    """
    Abstract class to provide API for all device drivers.

    Subclass and implement _connect, _read, _write, and _close, and define done_values.
    """

    done_values = []

    def __init__(self, loop):
        self.loop = loop
        self._connected = asyncio.Event(loop=loop)
        self._connecting = False
        self.log = logger(self.__class__.__name__)

    async def connect(self):
        """
        Safely connect to device, ensuring only one connection.
        """
        if not self._connected.is_set() and \
                not self._connecting:
            self._connecting = True
            self.log.debug('connecting')
            await self._connect()
            self._connected.set()
            self.log.info('connected')
        else:
            self.log.debug('waiting for connection')
            await self._connected.wait()
            self.log.debug('connection ready')

    async def read(self):
        """
        Connect, if necessary, and read from device. _read must be supplied by subclass.
        """
        if not self._connected:
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
        self.log.debug('writing {}'.format(stroke))
        if not self._connected.is_set():
            await self.connect()
        await self._write(stroke)

    def close(self):
        self._connected.clear()
        self._connecting = False
        self._close()
        self.log.info('closed')

    async def _connect(self):
        raise NotImplementedError

    async def _read(self):
        raise NotImplementedError

    async def _write(self, stroke):
        raise NotImplementedError

    async def _close(self):
        raise NotImplementedError


class Mock_Driver(Base_Driver):

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
