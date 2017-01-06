"""
Simple API to handle all hardware communication.
"""

from .logger import logger

__author__ = "riggs"


async def connect(driver_factory, motions, stop_event, event_loop, **driver_kwargs):
    log = logger('device communication')

    driver = driver_factory(event_loop, **driver_kwargs)
    await driver.connect()

    async def loop():
        try:
            async for motion in motions:
                log.debug("writing {}".format(motion))
                await driver.write(motion)
                log.debug("waiting for motion to finish")
                await driver.motion_finished()
        finally:
            driver.close()

    loop_task = event_loop.create_task(loop())

    async def stop():
        await stop_event.wait()
        loop_task.cancel()

    return stop()
