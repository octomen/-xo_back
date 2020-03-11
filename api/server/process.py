# -*- coding: utf-8 -*-
import logging
import typing
from collections import defaultdict
from typing import Dict, List

from api.server.action import Action, EmitData
from api.server.connection import ConnectionInfo
from api.server.pipe import Pipe, SendPipe, EmitKey

if typing.TYPE_CHECKING:
    from api.server.schema import ISchema


logger = logging.getLogger(__name__)


class Process:
    def __init__(self, schema: 'ISchema'):
        self.schema = schema
        self.bindings: Dict[EmitKey, List[Pipe]] = defaultdict(list)
        self.pipes = {}
        self.sockets = {}
        self.subscribers = {}

    async def handle_open(self, info: ConnectionInfo):
        socket_id = self.get_socket_id(info)

        if socket_id in self.sockets:
            raise Exception(f'Such client already exists: path = {info.path}')
        logger.info(f'connection open: {socket_id}')

        self.sockets[socket_id] = info.websocket

        pipe = SendPipe(socket_id, self)
        self.pipes[pipe.id] = pipe
        bindings = self.schema.create_entity(info.get_entity_type(), pipe)
        for emit_key, pipes in bindings.items():
            self.bindings[emit_key].extend(pipes)

    async def handle_close(self, info: ConnectionInfo):
        raise NotImplemented()

    async def handle_message(self, pipe_type: str,  message: str):
        logger.info(f'receive message: {message}')
        try:
            action = Action.from_json(message)
            emit_data = EmitData(pipe_type, action)
            await self.emit(emit_data)
        except Exception:
            logger.exception('except error while receive message')
            raise

    async def emit(self, emit_data: EmitData):
        for pipe in self.bindings.get(emit_data.get_key(), []):
            await pipe.emit(emit_data)

    async def send_message(self, socket_id: int, action: Action):
        websocket = self.sockets[socket_id]
        await websocket.send(action.serialize())

    async def emit_subscribers(self, pipe_id: int, action: Action):
        for subscriber in self.subscribers.get(pipe_id, []):
            await subscriber(action)

    @staticmethod
    def get_socket_id(info):
        # TODO: some more smart
        return info.path
