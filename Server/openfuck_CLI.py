import argparse
import asyncio
import sys

sys.path.append('.')

from openfuck import *

__author__ = "riggs"

def serial(arg):
    try:
        return {'baudrate': int(arg)}
    except ValueError:
        return {'url': "hwgrep://{}".format(arg)}


parser = argparse.ArgumentParser(description="Make machine go fuck.")
# TODO: Verbosity setting logging levels
parser.add_argument("--host", help="host address to listen for websockets connections")
parser.add_argument("--port", help="port used for websockets connections", type=int)
parser.add_argument("--mock", help="Use Mock driver (testing or development)", action="store_const", dest='driver',
                    const=Mock_Driver)
group = parser.add_argument_group("Serial Options", "Configure path and baud rate for serial connections")
group.add_argument("--switch", help="path to serial device and baud rate for solenoid-driven switch", nargs="*",
                   type=serial)
group.add_argument("--valves", help="path to serial device and baud rate for flow control valves", nargs="*",
                   type=serial)


def main(host='127.0.0.1', port=6969, driver=Serial_Driver, **kwargs):
    event_loop = asyncio.get_event_loop()
    stop_event = asyncio.Event(loop=event_loop)

    clean_up = set_up(host=host, port=port, driver=driver, stop_event=stop_event, event_loop=event_loop, **kwargs)

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        # Cleanup.
        stop_event.set()
        event_loop.run_until_complete(clean_up)


if __name__ == "__main__":
    parsed = parser.parse_args()

    kwargs = {}
    for key, value in vars(parsed).items():
        if value is None:
            continue
        if key in ['switch', 'valves']:
            args = {}
            for i in value:
                print(i)
                args.update(i)
            kwargs.setdefault('driver_kwargs', {})[key] = value
        else:
            kwargs[key] = value

    main(**kwargs)
