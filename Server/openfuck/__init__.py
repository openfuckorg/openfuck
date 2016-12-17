"""
The Master of Control
"""

import asyncio

from . import device
from . import websockets
from .data_model import *
from .logger import logger

__author__ = "riggs"

event_loop = asyncio.get_event_loop()

stop_event = asyncio.Event(loop=event_loop)


class Master_Pattern(Sub_Pattern):
    def __init__(self, *args, running=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = running
        self.updated = asyncio.Event()
        self.iterable = iter(self)
        self.log = logger(self.__class__.__name__)

    @staticmethod
    def _validate_cycles(cycles):
        if not cycles > 0:
            raise ValueError("cycles must be greater than 0")
        return cycles

    def update(self, pattern):
        self.log.debug("Updating to {}".format(pattern))
        if isinstance(pattern, dict):
            return self.update(self.from_dict(pattern))
        self.cycles = pattern.cycles
        self.running = pattern.running
        self.actions = pattern.actions
        self.iterable = iter(self)
        self.updated.set()

    def __repr__(self):
        return "{}(cycles={}, running={}, actions={}".format(self.__class__.__name__, self.cycles, self.running,
                                                             self.actions)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if stop_event.is_set():
            raise StopAsyncIteration
        try:
            if not self.running:
                self.updated.clear()  # Clear event to wait for update.
                raise StopIteration
            stroke = self.iterable.__next__()
            self.updated.clear()
            return stroke
        except StopIteration:
            self.log.debug("{}, waiting for update".format("Sub_Pattern expended" if self.running else "not running"))
            # If updated event is triggered first, clear flag and loop recurse to get first Stroke from new pattern.
            # If stop event is triggered first, recurse and StopAsyncIteration will be called because flag is set.
            completed, pending = await asyncio.wait([self.updated.wait(), stop_event.wait()],
                                                    loop=event_loop, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:  # Clean up after yourself.
                task.cancel()
            self.updated.clear()
            return await self.__anext__()


current_pattern = Master_Pattern(running=False, cycles=1, actions=(Stroke(position=0, speed=0.5),))


# Device object/loop/thing and websockets server are given event_loop, stop_event and current_pattern.
# Device is also given Driver object to use (this easily allows for multiple hardware).
# Server updates current_pattern and sets the current_pattern.updated event flag.
# Device waits for flag, updates its next Stroke pointer. (Parse pattern as depth-first tree transversal + cycles)
# Device listens for done moving signal, sends next Stroke.

# This file basically just creates the shared data objects then adds everything to the event_loop and runs it.

def test():

    async def set_up():
        device_close = await device.connect(device.Mock_Driver, current_pattern, stop_event, event_loop)
        websockets_close = await websockets.connect('127.0.0.1', 6969, current_pattern, stop_event, event_loop)
        return device_close, websockets_close

    stop_coros = event_loop.run_until_complete(set_up())

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        # Cleanup.
        stop_event.set()
        event_loop.run_until_complete(asyncio.wait(stop_coros))

