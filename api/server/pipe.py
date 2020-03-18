# -*- coding: utf-8 -*-
from itertools import count

import typing

from api.server.action import Action, ActionType

if typing.TYPE_CHECKING:
    from api.server.process import Process


class Pipe:
    COUNTER = count()

    def __init__(self, type_: str, processor: 'Process'):
        self.id = next(self.COUNTER)
        self.type_ = type_
        self._processor = processor

    def __repr__(self):
        return f'<Pipe id={self.id:!r}>'

    async def emit(self, emit_data):
        await self._processor.emit(emit_data)


PipeType = str
EmitKey = typing.Tuple[PipeType, ActionType]


class SendPipe(Pipe):
    def __init__(self, socket_id, processor):
        self.socket_id = socket_id
        super().__init__(processor)

    async def emit(self, action: Action):
        await self._processor.send_message(self.socket_id, action)
        await super().emit(action)


class SubscribePipe(Pipe):
    async def emit(self, action: Action):
        await self._processor.emit_subscribers(self.id, action)
        await super().emit(action)
