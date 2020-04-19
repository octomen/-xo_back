# -*- coding: utf-8 -*-
import asyncio
import json

import websockets


async def recv_printer(websocket):
    while True:
        print(await websocket.recv())


async def sender(websocket):
    while True:
        msg = await asyncio.get_event_loop().run_in_executor(None, input, 'Choose the move:\n >>> ')
        data = json.dumps({"type": "MESSAGE", "payload": msg})
        await websocket.send(data)


async def hello():
    host = '127.0.0.1:8000'

    user_uid = 123
    uri = f'ws://{host}/chat/123/{user_uid}'
    async with websockets.connect(uri) as websocket:
        await asyncio.wait([sender(websocket), recv_printer(websocket)])


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(hello())
