# -*- coding: utf-8 -*-
import asyncio

import pytest

from api.aioclub.action import ActionType, Action
from api.aioclub.bots import Bot, Writer
from api.aioclub.room import Room


SAY = ActionType('SAY')
EMITTER = object()


class BotForTest(Bot):
    def __init__(self, numder):
        self.numder = numder
        super().__init__()

    async def receive(self, writer: Writer):
        for i in range(4):
            await writer.write(SAY(f'HELLO_{i}_{self.numder}'))
            await asyncio.sleep(0)

    async def send(self, action: Action):
        print(action)


class Log:
    def __init__(self):
        self.data = []

    async def log_one(self, _, action):
        self.data.append(action)
        await asyncio.sleep(0.01)


@pytest.mark.asyncio
async def test_subscribe(bus, room: Room):
    log = Log()
    room.subscribe(EMITTER, SAY, log.log_one)

    actions = [
        SAY('hello'),
        SAY('I am Frankie'),
        SAY('Sinatra, yes'),
    ]

    for action in actions:
        await room.emit(EMITTER, action)

    await bus.join_until_empty()

    assert actions == log.data


@pytest.mark.asyncio
async def test_unsubscribe(bus, room: Room):
    hello = SAY('hello')
    bye = SAY('bye')

    log = Log()

    room.subscribe(EMITTER, SAY, log.log_one)
    await room.emit(EMITTER, hello)
    await bus.join_until_empty()

    room.unsubscribe(EMITTER, SAY, log.log_one)
    await room.emit(EMITTER, bye)
    await bus.join_until_empty()

    assert [hello] == log.data


@pytest.mark.asyncio
async def test_bot(bus, room: Room):
    log = Log()

    bot = BotForTest(1)
    room.subscribe(bot, SAY, log.log_one)
    room.register_bot(bot)
    await asyncio.sleep(0.1)
    await bus.join_until_empty()

    for i, action in enumerate(log.data):
        assert f'HELLO_{i}_1' == action.payload
