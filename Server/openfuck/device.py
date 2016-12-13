"""
Handle all hardware communication.
"""

import asyncio
from concurrent.futures import FIRST_COMPLETED

from .hardware_drivers import Driver
from .hardware_drivers import Test_Driver
from .logger import logger

__author__ = "riggs"

log = logger('device')


async def coroutine(driver, stroke_coro, loop, stop_future):
    stroke = None
    log.debug('creating initial read_task')
    read_task = loop.create_task(driver.read())
    log.debug('creating initial stroke_task')
    stroke_task = loop.create_task(stroke_coro())
    while not stop_future.done():
        log.debug('waiting for tasks')
        completed, pending = await asyncio.wait((read_task, stroke_task), loop=loop, return_when=FIRST_COMPLETED)
        if read_task in completed:
            log.debug('read_task completed')
            if read_task.result() and stroke:
                log.debug('writing {} to driver'.format(stroke))
                await driver.write(stroke)
            read_task = asyncio.ensure_future(driver.read())
        if stroke_task in completed:
            log.debug('stroke_task completed')
            stroke = stroke_task.result()
            log.debug('set stroke to {}'.format(stroke))
            stroke_task = asyncio.ensure_future(stroke_coro())
    else:
        driver.close()


async def connect(stroke_coro, loop, stop_future):
    # loop.create_task(coroutine(Driver(loop), stroke_coro, loop, stop_future))
    loop.create_task(coroutine(Test_Driver(loop), stroke_coro, loop, stop_future))
