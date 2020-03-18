# -*- coding: utf-8 -*-
import asyncio

import requests
import websockets


async def recv_printer(websocket):
    while True:
        print(await websocket.recv())


async def sender(websocket):
    while True:
        msg = await asyncio.get_event_loop().run_in_executor(None, input, 'Choose the move:\n')
        print(f"> {msg}")
        await websocket.send(msg)


async def hello():
    host = '127.0.0.1:8765'

    # resp = requests.get(f'http://{host}/chat/create')

    # user_uid = input('Type user uid:\n')
    user_uid = 123
    uri = f'ws://{host}/chat/123/user/{user_uid}'
    # uri = "ws://46.48.74.10:8000/game/123/{}".format(user_uid)
    async with websockets.connect(uri) as websocket:
        await asyncio.wait([sender(websocket), recv_printer(websocket)])


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(hello())
