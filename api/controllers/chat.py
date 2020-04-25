# -*- coding: utf-8 -*-
import logging

from api.actions import MESSAGE
from api.aioclub.action import Action
from api.aioclub.room import Room

log = logging.getLogger(__name__)


class Chat:
    def __init__(self, room: Room):
        self.room = room
        self.bots = {}

    def add_bot(self, uid, bot):
        self.bots[uid] = bot
        self.room.register_bot(bot)
        self.room.subscribe(bot, MESSAGE, self.say)

    async def say(self, emit_bot, action: Action):
        for bot in self.bots.values():
            if bot != emit_bot:
                await bot.send(action)
