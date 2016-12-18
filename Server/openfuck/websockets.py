"""
Manage communications with web clients.
"""
import asyncio

import websockets

from .logger import logger
from .data_model import deserialize, Query

__author__ = "riggs"

clients = set()

log = logger('websockets')


async def connect(host, port, motion_controller, stop_event, event_loop, **kwargs):
    stop_task = event_loop.create_task(stop_event.wait())
    listener_task = None

    async def handler(websocket, path):
        """"
        Called once per open connection.
        """
        nonlocal listener_task
        log = logger("websocket:{}:{}".format(id(websocket), path))
        log.debug("connected")
        clients.add(websocket)
        try:
            while not stop_event.is_set():
                listener_task = event_loop.create_task(websocket.recv())
                completed, pending = await asyncio.wait([listener_task, stop_task],
                                                        loop=event_loop, return_when=asyncio.FIRST_COMPLETED)
                if stop_task in completed:
                    listener_task.cancel()
                    log.debug("stopping")
                    break

                if listener_task in completed:
                    try:
                        data = listener_task.result()
                    except websockets.exceptions.ConnectionClosed:
                        break
                    finally:
                        listener_task = None
                    log.debug("received: {}".format(data))
                    try:
                        thing = deserialize(data)
                    except (TypeError, ValueError) as error:
                        log.debug("invalid data: {}, {}".format(type(error), error))
                        continue
                    if isinstance(thing, Query):
                        if thing.pattern:
                            thing.pattern = motion_controller.pattern
                        if thing.stroke:
                            thing.stroke = motion_controller.current_stroke
                        event_loop.create_task(websocket.send(thing.serialize()))
                        continue
                    if thing == motion_controller.pattern:  # No difference, don't reset iteration.
                        continue
                    motion_controller.update(thing)
                    log.debug("sending change to other clients")
                    for client in clients - {websocket, }:
                        event_loop.create_task(client.send(data))

        finally:
            clients.remove(websocket)

    server_coro = websockets.serve(handler, host, port, subprotocols=['openfuck'], **kwargs)
    log.debug("crated server listening on {}:{}".format(host, port))
    server_task = event_loop.create_task(server_coro)

    async def stop():
        await stop_event.wait()
        log.debug("closing")
        if listener_task is not None:
            listener_task.cancel()
        server = server_task.result()
        stop_task.cancel()
        server.close()
        await server.wait_closed()

    return stop()
