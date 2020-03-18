# -*- coding: utf-8 -*-
import logging
import typing
from collections import defaultdict
from itertools import count
from typing import Dict, List

from api.server.action import Action
from api.server.connection import ConnectionInfo
from api.server.pipe import SendPipe
from api.server.schema import Schema, EmitData


logger = logging.getLogger(__name__)


def emit(entity, action):
    emit_data = EmitData(entity._self__type, action)
    entity._self__process.emit(emit_data)


def send(entity, action):
    entity._server__process.send(entity._server__socket_id, action)


class ProcessKey:
    def __init__(self, websocket, path: str):
        self.websocket = websocket
        self.path = path
        self.splitted_path = self.path.split('/')[1:]

    @property
    def type(self):
        return self.splitted_path[0]

    @property
    def process_key(self):
        return tuple(self.splitted_path[:2])

    @property
    def entity_type(self):
        return self.splitted_path[2]


class Process:
    def __init__(self, schema: 'Schema'):
        self.schema = schema
        self.obj = schema.create()
        self.entities = {}
        self.entity_by_type = {}
        self.sockets = {}

    async def handle_open(self, info: ProcessKey):
        socket_id = self.get_socket_id(info)

        if socket_id in self.sockets:
            raise Exception(f'Such client already exists: path = {info.path}')
        logger.info(f'connection open: {socket_id}')

        self.sockets[socket_id] = info.websocket

        entity = self.schema.create_entity(info.entity_type)
        entity._self__process = self
        self.entities[socket_id] = entity
        await self.emit()

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
        await self.schema.handle(
            emit_data.entity_type,
            self.entity_by_type[emit_data.entity_type],
        )

    async def send(self, socket_id: int, action: Action):
        websocket = self.sockets[socket_id]
        await websocket.send(action.to_json())

    async def emit_subscribers(self, pipe_id: int, action: Action):
        for subscriber in self.subscribers.get(pipe_id, []):
            await subscriber(action)

    @staticmethod
    def get_socket_id(info):
        # TODO: some more smart
        return info.path


class ProcessStorage:
    def __init__(self):
        self.counter = count()
        self.process_type = {}
        self.processes = {}

    def register_scope(self, schema: Schema):
        self.process_type[schema.get_route()] = schema

    def get(self, type_, uid) -> Process:
        router_key = (type_, uid)

        # TODO: remove after implement registering new process
        if router_key not in self.processes:
            scope = self.process_type[type_]
            self.processes[router_key] = Process(scope)
        return self.processes[router_key]

    def create(self, type_):
        router_key = (type_, self.new_uid())
        scope = self.process_type[type_]
        self.processes[router_key] = Process(scope)

    def new_uid(self):
        return next(self.counter)