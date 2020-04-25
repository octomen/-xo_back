# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Hashable

from api.aioclub.bots import Writer, Bot
from api.aioclub.action import Action, ActionType
from api.aioclub.event_bus import EventBus, Subscriber

log = logging.getLogger(__name__)


class RoomWriter(Writer):
    def __init__(self, bot: Bot, bus: EventBus):
        self.bot = bot
        self.bus = bus

    async def write(self, action: Action):
        await self.bus.emit(self.bot, action)


class Room:
    def __init__(self, bus: EventBus):
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
            asyncio.create_task(
                bot.receive(writer)
            )
        )

    async def emit(self, emitter: Hashable, action: Action):
        await self.bus.emit(emitter, action)


class RoomFactory:
    def __init__(self, bus: EventBus):
        self._bus = bus

    def create_room(self):
        return Room(self._bus)
