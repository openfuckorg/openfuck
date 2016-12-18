__author__ = "riggs"

import asyncio
import sys

sys.path.append('.')

from openfuck import *


def main():
    event_loop = asyncio.get_event_loop()
    stop_event = asyncio.Event(loop=event_loop)

    set_up(host='127.0.0.1', port=6969, driver=Serial_Driver, stop_event=stop_event, event_loop=event_loop)

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        # Cleanup.
        stop_event.set()


if __name__ == "__main__":
    main()
