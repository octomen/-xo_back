import asyncio
import logging
import hashlib
from typing import Callable

from api.modules.socket import WebSocketProxy
from . import Board

log = logging.getLogger(__name__)


class User:
    def __init__(self, socket: WebSocketProxy, uid: str):
        self.uid = uid
        self._socket = socket
        self._on_action = set()  # TODO: callback management
        self._on_disconnect = set()

    def __eq__(self, other):
        if not hasattr(other, 'uid'):
            return False
        return other.uid == self.uid

    def __hash__(self):
        return int(hashlib.sha1(self.uid.encode()).hexdigest(), 16)

    async def start_serve(self):
        async for message in self._socket:
            log.debug('User receive: {}'.format(message))
            await asyncio.wait([asyncio.ensure_future(c(self, message)) for c in self._on_action])  # TODO: message -> action object
        await asyncio.wait([asyncio.ensure_future(c(self)) for c in self._on_disconnect])

    def on_action(self, callback: Callable):
        self._on_action.add(callback)

    def on_disconnect(self, callback: Callable):
        self._on_disconnect.add(callback)

    async def send(self, data):
        await self._socket.send(data)  # TODO: data -> action object
