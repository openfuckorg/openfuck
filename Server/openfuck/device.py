"""
Handle all hardware communication.
"""

import asyncio
from concurrent.futures import FIRST_COMPLETED

from .logger import logger

__author__ = "riggs"

log = logger('device loop')


async def connect(driver_class, next_queue, done_queue, event_loop, stop_event):
    driver = driver_class(event_loop)
    stroke = None
    first_run = True
    stroke_done = asyncio.Event(loop=event_loop)
    log.debug('creating initial driver_read_task')
    driver_read_task = event_loop.create_task(driver.read())
    log.debug('creating initial next_stroke_task')
    next_stroke_task = event_loop.create_task(next_queue.get())
    log.debug('waiting for tasks')
    completed, pending = await asyncio.wait((driver_read_task, next_stroke_task), loop=event_loop, return_when=FIRST_COMPLETED)
    while not stop_event.is_set():
        if driver_read_task in completed:
            log.debug('driver_read_task completed')
            if driver_read_task.result() and stroke is not None:
                stroke_done.set()
                log.debug('set stroke_done event as done: {}({})'.format(stroke_done, id(stroke_done)))
                log.debug('writing {} to driver'.format(stroke))
                await driver.write(stroke)
            log.debug('creating new driver_read_task')
            driver_read_task = event_loop.create_task(driver.read())
        elif next_stroke_task in completed:
            log.debug('next_stroke_task completed')
            stroke = next_stroke_task.result()
            log.debug('got stroke from queue: {}'.format(stroke))
            stroke_done = asyncio.Event(loop=event_loop)
            log.debug('putting stroke_done event into queue: {}({})'.format(stroke_done, id(stroke_done)))
            event_loop.create_task(done_queue.put(stroke_done))
            log.debug('creating new next_stroke_task')
            next_stroke_task = event_loop.create_task(next_queue.get())
            if first_run:
                first_run = False
                log.debug('writing {} to driver'.format(stroke))
                await driver.write(stroke)
        log.debug('waiting for tasks')
        completed, pending = await asyncio.wait((driver_read_task, next_stroke_task), loop=event_loop, return_when=FIRST_COMPLETED)
    else:
        for task in pending:
            task.cancel()
        driver.close()
