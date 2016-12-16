"""
Manage communications with web clients.
"""
import asyncio

import websockets

from .data_model import Pattern
from .logger import logger

__author__ = "riggs"

clients = set()

log = logger('websockets')

async def connect(host, port, current_pattern, stop_event, event_loop):
    async def handler(websocket, path):
        """"
        Called once per open connection.
        """
        log = logger("websocket_{}_{}".format(id(websocket), path))
        log.debug("connected")
        clients.add(websocket)
        try:
            stop_task = event_loop.create_task(stop_event.wait())
            while not stop_event.is_set():
                listener_task = event_loop.create_task(websocket.recv())
                completed, pending = await asyncio.wait([listener_task, stop_task],
                                                        loop=event_loop, return_when=asyncio.FIRST_COMPLETED)
                if stop_task in completed:
                    listener_task.cancel()
                    log.debug("stopping")
                    break

                if listener_task in completed:
                    data = listener_task.result()
                    log.debug("received:\n{}".format(data))
                    current_pattern.update(Pattern.deserialize(data))
                    for client in clients - {websocket, }:
                        event_loop.create_task(client.send(data))

        finally:
            clients.remove(websocket)

    server = websockets.serve(handler, host, port, subprotocols=['openfuck'])
    log.debug("crated server listening on {}:{}".format(host, port))
    event_loop.create_task(server)
