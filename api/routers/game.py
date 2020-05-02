# -*- coding: utf-8 -*-
import logging
import uuid

from fastapi import FastAPI
from starlette.websockets import WebSocket

from api.actions import ERROR, DISCONNECT
from api.aioclub.bots.starlette_websocket_bot import StarletteWebSocketBot
from api.aioclub.room import RoomFactory
from api.controllers import User, Game
from api.modules.storage import DataSource
from api.utils.http import success_response

logger = logging.getLogger(__name__)


class Router:
    def __init__(self, storage: DataSource, room_factory: RoomFactory):
        self.storage = storage
        self.room_factory = room_factory

    def register_routes(self, app: FastAPI):
        app.post(path='/game')(self.create_game)
        app.websocket(path='/game/{game_uid}/{user_uid}')(self.connect_as_gamer)

    def create_game(self):
        uid = str(uuid.uuid4())
        self.storage.set(
            key=uid,
            value=Game(
                room=self.room_factory.create_room()
            ),
        )
        logger.info('create game %s', uid)
        return success_response({
            'uid': uid,
        })

    async def connect_as_gamer(self, websocket: WebSocket, game_uid: str, user_uid: str):
        logger.info('Got connection for game_uid=%s, user_uid=%s', game_uid, user_uid)
        await websocket.accept()
        bot = StarletteWebSocketBot(websocket)
        user = User(user_uid, bot)

        game_ctl = self.storage.get(game_uid)
        if not game_ctl:
            logger.info('Client requested unregistered game %s', game_uid)
            await websocket.send_json(
                ERROR(f'Game (id={game_uid}) does not exist').to_dict()
            )
            await websocket.close()
            return

        game_ctl.add_gamer(user)
        logger.info('added bot')
        await bot.join()
        game_ctl.room.emit(user, DISCONNECT)
        logger.info('connection broke')
