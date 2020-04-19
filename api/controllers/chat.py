# -*- coding: utf-8 -*-
import logging

from api.aioclub.action import Action, ActionType
from api.aioclub.room import RoomFactory, Room
from api.modules.main import storage

log = logging.getLogger(__name__)
MESSAGE = ActionType('MESSAGE')


class Chat:
    def __init__(self, room: Room):
        self.room = room
        self.bots = {}

    def add_bot(self, uid, bot):
        self.bots[uid] = bot
        self.room.register_bot(bot)
        self.room.subscribe(bot, MESSAGE, self.say)

    async def say(self, action: Action):
        print(action)


def get_or_create(chat_uid: str) -> Chat:
    game = storage.get(chat_uid)
    if not game:
        return storage.set(chat_uid, Chat(
            RoomFactory().create_room()
        ))
    return game
