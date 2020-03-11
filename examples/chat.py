# -*- coding: utf-8 -*-
from api.server.action import Action
from api.server.schema import Entity, Schema
from api.server.server import Server

SAY = Action('SAY')


class CHAT(Schema):
    USER = Entity()
    WATCHER = Entity()


schema = CHAT()


@schema.ENTRYPOINT
class Chat:
    def __init__(self):
        self.users = []

    @schema.CREATE(schema.USER)
    def new_user(self, entity):
        self.users.append(entity)

    @schema.METHOD(schema.USER, actions=[SAY])
    async def say(self, entity: Entity, payload):
        for player in self.players:
            if player == entity:
                continue
            await player.emit(SAY(payload))


@schema.WATCHER
class WatcherImplementation:
    @schema.METHOD(schema.USER, actions=[SAY])
    def notify(self, _: Entity, payload):
        self.entity.emit(SAY(payload))


schema.BIND(schema.WATCHER, actions=[SAY])(print)


if __name__ == '__main__':
    server = Server()
    server.register_schema(schema)
    server.run()
