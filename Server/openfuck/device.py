"""
Simple API to handle all hardware communication.
"""

from .logger import logger

__author__ = "riggs"


async def connect(driver_class, motion_controller, stop_event, event_loop, **kwargs):
    log = logger('device communication')

    driver = driver_class(event_loop, **kwargs)
    await driver.connect()

    async def loop():
        try:
            async for motion in motion_controller:
                log.debug("writing {}".format(motion))
                await driver.write(motion)
                log.debug("waiting for motion to finish")
                await driver.stroke_finished()
        finally:
            driver.close()

    loop_task = event_loop.create_task(loop())

    async def stop():
        await stop_event.wait()
        loop_task.cancel()

    return stop()
