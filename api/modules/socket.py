import json
from starlette.websockets import WebSocket, WebSocketDisconnect


class WebSocketProxy:
    def __init__(self, websocket: WebSocket):
        self._websocket = websocket

    async def receive(self):
        return await self._websocket.receive_text()

    async def send(self, data):
        await self._websocket.send_text(self._serialize(data))

    async def __aiter__(self):
        try:
            while True:
                yield self._deserialize(await self.receive())
        except WebSocketDisconnect:
            pass

    def _serialize(self, data):
        return json.dumps(data, ensure_ascii=False)

    def _deserialize(self, data: str):
        return json.loads(data)
