import asyncio

from ..logger import logger
from ..data_model import Wait

__author__ = "riggs"


class Base_Driver:
    """
    Abstract class to provide API for all device drivers.

    Subclass and implement _connect, _read, _write, and _close, and define done_values.
    """

    done_values = NotImplemented

    def __init__(self, loop, **kwargs):
        self.loop = loop
        self._connected = asyncio.Event(loop=loop)
        self._connecting = False
        self._wait = asyncio.Event(loop=loop)
        self._tasks = {loop.create_task(self._wait.wait()), }
        self._read_task = None
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
        self._read_task = self.loop.create_task(self.read())
        self._tasks.add(self._read_task)

    async def read(self):
        """
        Connect, if necessary, and read from device. _read must be supplied by subclass.
        """
        if not self._connected:
            self.log.debug('read connecting')
            await self.connect()
        self.log.debug('reading')
        return await self._read()

    async def motion_finished(self):
        """
        Wait until device sends 'done moving' value, then return True, discarding any other values read.
        """
        completed, pending = await asyncio.wait(self._tasks, loop=self.loop, return_when=asyncio.FIRST_COMPLETED)
        self._tasks -= completed
        if self._read_task in completed:
            value = self._read_task.result()
            self._read_task = self.loop.create_task(self.read())
            self._tasks.add(self._read_task)
            if value in self.done_values:
                return True
            else:
                return await self.motion_finished()
        else:
            self._wait.clear()
            self._tasks.add(self.loop.create_task(self._wait.wait()))
            return True

    async def write(self, motion):
        if isinstance(motion, Wait):
            self.log.debug("Waiting {}".format(motion))
            return self.loop.call_later(motion.duration, self._wait.set)
        self.log.debug('writing {}'.format(motion))
        if not self._connected.is_set():
            await self.connect()
        await self._write(motion)

    def close(self):
        self._connected.clear()
        self._connecting = False
        self._close()
        for task in self._tasks:
            task.cancel()
        self.log.info('closed')

    async def _connect(self):
        raise NotImplementedError

    async def _read(self):
        raise NotImplementedError

    async def _write(self, stroke):
        raise NotImplementedError

    async def _close(self):
        raise NotImplementedError


