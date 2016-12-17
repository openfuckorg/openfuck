__author__ = "riggs"

import asyncio
import sys

import websockets

sys.path.append('.')

from openfuck import device, current_pattern, stop_event, event_loop


def main():
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


if __name__ == "__main__":
    main()
