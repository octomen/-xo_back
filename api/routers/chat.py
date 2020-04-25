# -*- coding: utf-8 -*-
import logging
import uuid

from fastapi import FastAPI
from starlette.websockets import WebSocket

from api.actions import ERROR
from api.aioclub.bots.starlette_websocket_bot import StarletteWebSocketBot
from api.aioclub.room import RoomFactory
from api.controllers.chat import Chat
from api.modules.storage import DataSource
from api.utils.http import success_response

logger = logging.getLogger(__name__)


class Router:
    def __init__(self, storage: DataSource, room_factory: RoomFactory):
        self.storage = storage
        self.room_factory = room_factory

    def register_routes(self, app: FastAPI):
        app.post(path='/chat')(self.create_room)
        app.websocket(path='/chat/{chat_uid}/{user_uid}')(self.connect_as_user)

    def create_room(self):
        uid = str(uuid.uuid4())
        self.storage.set(
            key=uid,
            value=Chat(
                room=self.room_factory.create_room()
            ),
        )
        logger.info('create chat %s', uid)
        return success_response({
            'uid': uid,
        })

    async def connect_as_user(self, websocket: WebSocket, chat_uid: str, user_uid: str):
        logger.info('Got connection for chat_uid=%s, user_uid=%s', chat_uid, user_uid)
        await websocket.accept()
        bot = StarletteWebSocketBot(websocket)

        chat_ctl = self.storage.get(chat_uid)
        if not chat_ctl:
            logger.info('Client requested unregistered chat %s', chat_uid)
            await websocket.send_json(
                ERROR(f'Chat (id={chat_uid}) does not exist').to_dict()
            )
            await websocket.close()
            return

        chat_ctl.add_bot(user_uid, bot)
        logger.info('added bot')
        await bot.join()
        logger.info('connection broke')
