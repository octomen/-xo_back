# -*- coding: utf-8 -*-
from api.server.action import ActionType, CREATE
from api.server.schema import Entity, EntityType, Schema, METHOD, BIND

SAY = ActionType('SAY')


class CHAT(Schema):
    USER: EntityType
    WATCHER: EntityType


@CHAT
class _:
    def __init__(self):
        self.users = []

    @METHOD(CHAT.USER, actions=[CREATE])
    def new_user(self, entity, _):
        self.users.append(entity)

    @METHOD(CHAT.USER, actions=[SAY])
    async def say(self, entity: Entity, payload):
        for player in self.players:
            if player == entity:
                continue
            await player.emit(SAY(payload))


@CHAT.WATCHER
class WatcherImplementation:
    @METHOD(CHAT.USER, actions=[SAY])
    def notify(self, _: Entity, payload):
        self.entity.emit(SAY(payload))


BIND(CHAT.WATCHER, actions=[SAY])(print)


if __name__ == '__main__':
    from api.server.server import Server
    from api.server.process import ProcessStorage

    server = Server(ProcessStorage())
    server.register_schema(CHAT)
    server.run()
