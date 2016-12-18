"""
The Master of Control
"""
import asyncio

from . import data_model
from . import device
from . import serial_drivers
from . import websockets
from .data_model import *
from .logger import logger

__author__ = "riggs"

__all__ = ("set_up", "Motion_Controller") + serial_drivers.__all__ + data_model.__all__


class Motion_Controller:
    def __init__(self, stop_event, event_loop=None, pattern=Pattern(cycles=1, motions=(Wait(duration=2 ** 32 - 1),))):
        self.loop = event_loop if event_loop is not None else asyncio.get_event_loop()
        self.stop_event = stop_event
        self.stop_task = self.loop.create_task(self.stop_event.wait())
        self.pattern = pattern
        self.iterable = iter(self.pattern)
        self.updated = asyncio.Event()
        self.tasks = {self.stop_task,}
        self.log = logger(self.__class__.__name__)

    def update(self, pattern):
        self.log.debug("Updating to {}".format(pattern))
        self.pattern = pattern
        self.iterable = iter(pattern)
        self.updated.set()

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.stop_event.is_set():
            raise StopAsyncIteration
        try:
            return self.iterable.__next__()
        except StopIteration:
            self.log.debug("Pattern expended, waiting for update")
            # If updated event is triggered first, clear flag and loop recurse to get first Stroke from new pattern.
            # If stop event is triggered first, recurse and StopAsyncIteration will be called because flag is set.
            update_task = self.loop.create_task(self.updated.wait())
            self.tasks.add(update_task)
            completed, pending = await asyncio.wait(self.tasks, loop=self.loop, return_when=asyncio.FIRST_COMPLETED)
            self.tasks -= completed
            self.updated.clear()  # If stop was triggered, this has no effect, anyway.
            return await self.__anext__()

    async def stop(self):
        await self.stop_event.wait()
        for task in self.tasks:
            task.cancel()


def set_up(host, port, driver, stop_event=None, event_loop=None, **kwargs):
    """
    Connect to the hardware, create the websockets server and connect them.

    :param host: Internet host to connect to and listen for new websockets connections.
    :param port: Port to listen on.
    :param driver: Hardware driver to use for hardware connection.
    :param stop_event: Setting the flag on this event will cause the server to shut down and clean.
    :param event_loop: Event loop which controls execution.
    :param kwargs: Additional arguments passed through to the driver and websockets server (e.g. for configuring TLS).
    :type host: str
    :type stop_event: asyncio.Event
    :type event_loop: asyncio.AbstractEventLoop
    :return: A clean-up coroutine. Pass to event_loop.run_until_complete after calling stop_event.set().
    """
    if event_loop is None:
        event_loop = asyncio.get_event_loop()

    motion_controller = Motion_Controller(event_loop=event_loop, stop_event=stop_event,
                                          pattern=Pattern(cycles=5, motions=(Wait(duration=3),)))

    async def start():
        device_close = await device.connect(driver, motion_controller, stop_event, event_loop, **kwargs)
        websockets_close = await websockets.connect(host, port, motion_controller, stop_event, event_loop, **kwargs)
        return {device_close, websockets_close}

    stop_coros = event_loop.run_until_complete(start())
    stop_coros.add(motion_controller.stop())

    return asyncio.wait(stop_coros)


def test():
    event_loop = asyncio.get_event_loop()
    stop_event = asyncio.Event(loop=event_loop)

    clean_up = set_up(host='127.0.0.1', port=6969, driver=device.Mock_Driver,
                      stop_event=stop_event, event_loop=event_loop)

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        # Cleanup.
        stop_event.set()
        event_loop.run_until_complete(clean_up)
