"""
The Master of Control
"""

import asyncio

from . import device
from .data_model import *

__author__ = "riggs"

event_loop = asyncio.get_event_loop()

stop_event = asyncio.Event(loop=event_loop)


class Current_Pattern(Pattern):

    updated = asyncio.Event()
    lock = asyncio.Lock(loop=event_loop)

    async def update(self, pattern):
        if isinstance(pattern, dict):
            return self.update(super().from_dict(pattern))
        await self.lock.acquire()
        self.repeat = pattern.repeat
        self.actions = pattern.actions
        self._reset_state()
        self.lock.release()
        return self

    def _reset_state(self):
        self._iter_actions_index = 0
        self._iter_repeat_count = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        await self.lock.acquire()
        stroke = self.__next__()
        self.lock.release()
        return stroke


current_pattern = Current_Pattern(repeat=0, actions=(Stroke(position=0, speed=0.5),))


# Device object/loop/thing and websockets server are given event_loop, stop_event and current_pattern.
# Device is also given Driver object to use (this easily allows for multiple hardware).
# Server updates current_pattern and sets the current_pattern.updated event flag.
# Device waits for flag, updates its next Stroke pointer. (Parse pattern as depth-first tree transversal + repeats)
# Device listens for done moving signal, sends next Stroke.

# This file basically just creates the shared data objects then adds everything to the event_loop and runs it.

# Mostly works. Helped me figure out the proper architecture.
# Will throw away later.
def test():
    from .hardware_drivers import Test_Driver
    from .data_model import Stroke
    from .logger import logger

    log = logger('test app')

    next_stroke_queue = asyncio.Queue()
    stroke_done_queue = asyncio.Queue()

    async def delay(seconds, func):
        await asyncio.sleep(seconds)
        return func()

    async def send_strokes(strokes):
        log.debug('input: {}'.format(strokes))
        while strokes:
            stroke = strokes.pop(0)
            log.debug('putting in next_stroke_queue: {}'.format(stroke))
            event_loop.create_task(next_stroke_queue.put(stroke))
            log.debug('waiting for stroke_done event from stroke_done_queue')
            stroke_done = await stroke_done_queue.get()
            log.debug('waiting for stroke_done event to finish: {}({})'.format(stroke_done, id(stroke_done)))
            await stroke_done.wait()
        log.debug('setting stop_event {}({})'.format(stop_event, id(stop_event)))
        stop_event.set()

    event_loop.create_task(device.old_connect(Test_Driver, next_stroke_queue, stroke_done_queue, event_loop, stop_event))

    event_loop.create_task(send_strokes([Stroke(i / 10, i / 10) for i in range(3)]))

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        pass
