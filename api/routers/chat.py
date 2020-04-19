# -*- coding: utf-8 -*-
import logging

from fastapi import FastAPI
from starlette.websockets import WebSocket

from api.aioclub.bots.starlette_websocket_bot import StarletteWebSocketBot
from api.controllers import chat

logger = logging.getLogger(__name__)

app = FastAPI()


@app.websocket(path='/chat/{chat_uid}/{user_uid}')
async def connect_as_gamer(websocket: WebSocket, chat_uid: str, user_uid: str):
    await websocket.accept()
    bot = StarletteWebSocketBot(websocket)

    chat_ctl = chat.get_or_create(chat_uid)
    chat_ctl.add_bot(user_uid, bot)
    logger.info('added bot')
    await bot.join()
    logger.info('connection broke')
