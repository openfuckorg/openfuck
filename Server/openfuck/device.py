"""
Handle all hardware communication.
"""

import asyncio
import logging
import sys
from concurrent.futures import FIRST_COMPLETED

from .hardware_drivers import switch, valves

__author__ = "riggs"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr,
)
log = logging.getLogger('device')


async def coro_factory(driver, stroke_coro, loop, stop_future):
    stroke = None
    read_task = asyncio.ensure_future(driver.read())
    stroke_task = asyncio.ensure_future(stroke_coro())
    while not stop_future.done():
        completed, pending = await asyncio.wait((read_task, stroke_task), loop=loop, return_when=FIRST_COMPLETED)
        if read_task in completed:
            if read_task.result() and stroke:
                await driver.write(stroke)
            read_task = asyncio.ensure_future(driver.read())
        if stroke_task in completed:
            stroke = stroke_task.result()
            stroke_task = asyncio.ensure_future(stroke_coro())
    else:
        driver.close()


async def connect(stroke_coro, loop, stop_future):
    loop.run_until_complete(coro_factory(switch, stroke_coro, loop, stop_future))
    loop.run_until_complete(coro_factory(valves, stroke_coro, loop, stop_future))
