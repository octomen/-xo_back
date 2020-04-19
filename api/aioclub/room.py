# -*- coding: utf-8 -*-
import asyncio
from typing import Hashable

from api.aioclub.bots import Writer, Bot
from api.aioclub.action import Action, ActionType
from api.aioclub.event_bus import EventBus, Subscriber


class RoomWriter(Writer):
    def __init__(self, bot: Bot, bus: EventBus):
        self.bot = bot
        self.bus = bus

    async def write(self, action: Action):
        await self.bus.emit(self.bot, action)


class Room:
    def __init__(self, loop: asyncio.AbstractEventLoop, bus: EventBus):
        self.loop = loop
        self.bus = bus

        # TODO: реализовать close в котором прибить таски
        self.tasks = []

    def subscribe(self, emitter: Hashable, action: ActionType, subscriber: Subscriber):
        self.bus.subscribe(emitter, action, subscriber)

    def unsubscribe(self, emitter: Hashable, action: ActionType, subscriber: Subscriber):
        self.bus.unsubscribe(emitter, action, subscriber)

    def register_bot(self, bot: Bot):
        writer = RoomWriter(bot, self.bus)
        self.tasks.append(
            self.loop.create_task(
                bot.receive(writer)
            )
        )

    async def emit(self, emitter: Hashable, action: Action):
        await self.bus.emit(emitter, action)


class RoomFactory:
    def __init__(self, loop: asyncio.AbstractEventLoop = None, bus: EventBus = None):
        self.loop = loop or asyncio.get_event_loop()
        self.bus = bus or EventBus(self.loop)
        self.bus.run()

    def create_room(self):
        return Room(self.loop, self.bus)
