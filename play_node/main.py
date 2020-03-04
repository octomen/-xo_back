# -*- coding: utf-8 -*-
import asyncio
import json
from contextlib import asynccontextmanager
from typing import Optional

import requests
import websockets

from play_node.setting import Setting


def message_from_raw(raw: str):
    print(raw)
    message = json.loads(raw)
    type_ = message.get('type')
    if type_ == 'STATE':
        return State(message['board'], message['currentUser'], message['x'] and message['y'])
    raise Exception


class State:
    def __init__(self, board, current, running):
        self.board = board
        self.current = current
        self.running = running


class Game:
    def __init__(self, settings: Setting):
        self.settings = settings
        self.socket: Optional[websockets] = None
        self._my_turn = False
        self._is_running = False
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    def sync_game(self, state: State):
        self.board = state.board
        self._my_turn = state.current
        self._is_running = state.running

    @property
    def my_turn(self):
        return self._my_turn

    def show(self):
        print(self.board)

    def is_running(self):
        return self._is_running

    @asynccontextmanager
    async def join(self):
        async with websockets.connect(self.settings.URL + '/game/123/asd') as socket:
            self.socket = socket
            yield

    async def wait_my_turn(self):
        while True:
            await self.update_state()

            if self.my_turn:
                return

    async def update_state(self):
        await asyncio.sleep(0.01)
        message = message_from_raw(await self.socket.recv())

        if isinstance(message, State):
            self.sync_game(message)
        else:
            raise Exception
        return

    async def wait_start(self):
        while True:
            await self.update_state()

            if self.is_running():
                return

    async def move(self, message):
        print(message)
        await self.socket.send(message)


async def test():
    # requests.get(Setting().URL + '')
    game = Game(Setting())
    async with game.join():
        await game.wait_start()
        while game.is_running():
            await game.wait_my_turn()
            game.show()
            await game.move(input('Your turn >>> '))
        game.show()


asyncio.get_event_loop().run_until_complete(test())
