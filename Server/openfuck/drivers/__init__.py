import asyncio

from ..base_driver import Base_Driver

# from . import serial_drivers
from .serial_drivers import *

__author__ = "riggs"


__all__ = ("Mock_Driver", ) + serial_drivers.__all__


class Mock_Driver(Base_Driver):
    """
    Simple example driver that simulates "movement" with a delay.
    """
    done_values = [True]

    def __init__(self, loop, **kwargs):
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
