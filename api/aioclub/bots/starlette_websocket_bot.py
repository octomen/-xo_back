# -*- coding: utf-8 -*-
import logging

from starlette.websockets import WebSocket, WebSocketDisconnect

from api.aioclub.action import Action
from api.aioclub.bots import Bot, Writer

log = logging.getLogger(__name__)


class StarletteWebSocketBot(Bot):
    def __init__(self, websocket: WebSocket):
        self._websocket = websocket
        super().__init__()

    async def receive(self, writer: Writer):
        """Потребляет сообщения из внешнего мира и пишет в шину"""
        log.info('start receiving')
        try:
            while self._is_alive:
                action = self._deserialize(await self.receive_message())
                log.debug('received action %s', action)
                if action:
                    await writer.write(action)
        except WebSocketDisconnect:
            log.info('socket disconnected')
            self._is_alive = False

    async def send(self, action: Action):
        """Отправляет сообщения во внешний мир"""
        if not self._is_alive:
            log.warning('Zombie bot %s continues to receive actions', self)
            return
        await self._websocket.send_text(action.to_json())

    async def receive_message(self):
        text = await self._websocket.receive_text()
        log.debug('received %s', text)
        return text

    @staticmethod
    def _deserialize(data: str):
        try:
            return Action.from_json(data)
        except Exception:
            log.exception('Catch exception while parsing message %s', data)
            raise
