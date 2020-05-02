# -*- coding: utf-8 -*-
from fastapi import FastAPI

from api import routers
from api.aioclub.event_bus import EventBus
from api.aioclub.room import RoomFactory
from api.modules.storage import DataSource


def create_app(bus=None):
    app = FastAPI()
    storage = DataSource()

    bus = bus or EventBus()
    chat_router = routers.chat.Router(storage, RoomFactory(bus))
    chat_router.register_routes(app)

    game_router = routers.game.Router(storage, RoomFactory(bus))
    game_router.register_routes(app)

    @app.on_event('startup')
    async def startup_event():
        bus.run()

    @app.get('/ping')
    def ping():
        return {
            'status': 'ok',
            'data': 'pong',
        }

    return app


app = create_app()
