"""
The Master of Control
"""

import asyncio
from concurrent.futures import FIRST_COMPLETED

from . import device
from .data_model import *
from .logger import logger

__author__ = "riggs"

event_loop = asyncio.get_event_loop()

stop_event = asyncio.Event(loop=event_loop)


class Current_Pattern(Pattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updated = asyncio.Event()
        self.iterable = iter(self)
        self.log = logger(self.__class__.__name__)

    def update(self, pattern):
        self.log.debug("Updating with {}".format(pattern))
        if isinstance(pattern, dict):
            return self.update(super().from_dict(pattern))
        self.cycles = pattern.cycles
        self.actions = pattern.actions
        self.iterable = iter(self)
        self.updated.set()

    def __aiter__(self):
        return self

    async def __anext__(self):
        if stop_event.is_set():
            raise StopAsyncIteration
        try:
            stroke = self.iterable.__next__()
            self.updated.clear()
            return stroke
        except StopIteration:
            self.log.debug("Pattern expended, waiting for update")
            # If updated event is triggered first, clear flag and loop recurse to get first Stroke from new pattern.
            # If stop event is triggered first, recurse and StopAsyncIteration will be called because flag is set.
            completed, pending = await asyncio.wait([self.updated.wait(), stop_event.wait()],
                                                    loop=event_loop, return_when=FIRST_COMPLETED)
            for task in pending:  # Clean up after yourself.
                task.cancel()
            self.updated.clear()
            return await self.__anext__()


current_pattern = Current_Pattern(cycles=1, actions=(Stroke(position=0, speed=0.5),))


# Device object/loop/thing and websockets server are given event_loop, stop_event and current_pattern.
# Device is also given Driver object to use (this easily allows for multiple hardware).
# Server updates current_pattern and sets the current_pattern.updated event flag.
# Device waits for flag, updates its next Stroke pointer. (Parse pattern as depth-first tree transversal + cycles)
# Device listens for done moving signal, sends next Stroke.

# This file basically just creates the shared data objects then adds everything to the event_loop and runs it.

def test():
    from functools import partial

    event_loop.call_later(0, partial(current_pattern.update, Pattern(2, [Stroke(.69, .69), Stroke(.42, .42)])))

    event_loop.call_later(8, partial(current_pattern.update,
                                     Pattern(float('inf'), [Stroke(0.1, 0.1), Stroke(0.2, 0.2), Stroke(0.3, 0.3)])))

    event_loop.call_later(12, stop_event.set)

    event_loop.create_task(device.connect(device.Mock_Driver, event_loop, current_pattern))

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        pass
