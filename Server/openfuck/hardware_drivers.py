"""
Hardware drivers used by device.py
"""
import attr
import serial
import serial.aio

__author__ = "riggs"

SWITCH = {'port': '/dev/ttyACM0', 'baudrate': 115200}
VALVES = {'port': '/dev/ttyACM1', 'baudrate': 115200}


@attr.s(frozen=True)
class Serial:
    reader = attr.ib()
    writer = attr.ib()

    @classmethod
    async def connect(cls, loop, port, baudrate):
        log.debug("connecting to {port} {baudrate}".format(port=port, baudrate=baudrate))
        return cls(*await serial.aio.open_serial_connection(loop=loop, port=port, baudrate=baudrate))


async def switch(stream_writer, stroke):
    data = bytes((int(stroke.position * 255),))
    stream_writer.write(data)
    await stream_writer.drain()

# TODO: Class driver

    connection = await Serial.connect(loop=loop, port=port, baudrate=baudrate)
