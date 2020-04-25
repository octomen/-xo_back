# -*- coding: utf-8 -*-
import asyncio
import json

import requests
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
    host = '0.0.0.0:8000'

    chat_uid = input('input chat uid or do nothing:')
    if not chat_uid:
        chat_uid = requests.post(f'http://{host}/chat').json()['data']['uid']
        print(f'New chat uid: {chat_uid}')

    user_uid = int(input('your no, please: '))
    uri = f'ws://{host}/chat/{chat_uid}/{user_uid}'
    async with websockets.connect(uri) as websocket:
        await asyncio.wait([sender(websocket), recv_printer(websocket)])


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(hello())
