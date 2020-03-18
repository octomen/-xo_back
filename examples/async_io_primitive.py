import asyncio
import websockets

from websockets.exceptions import ConnectionClosed


class User:
    def __init__(self, websocket, board):
        self._websocket = websocket
        self._board: 'Board' = board
        self._board.add_user(self)

    async def serve(self):
        done, pending = await asyncio.wait(
            [
                self._handle_recv(),
                self._ping(),
            ], return_when=asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()
        self._board.remove_user(self)

    async def _handle_recv(self):
        async for message in self._websocket:
            await self.on_receive_message(message)

    async def on_receive_message(self, message):
        print(self, message, 'MOVE! Write state')  # TODO: change board state
        await self._board.move(self, message)

    async def on_update_state(self, board):
        await self._websocket.send(str(board))  # TODO: serialize state / board ?


class Board:
    def __init__(self):
        self._users = []
        self._state = 0  # TODO: serialize state

    def add_user(self, user: User):  # TODO: rules
        self._users.append(user)

    def remove_user(self, user: User):
        self._users.remove(user)

    async def move(self, user: User, info):  # TODO: rules
        self._state += 1
        print('CHANGE STATE', user, info, self._state)
        await self.on_change_state()

    async def on_change_state(self):
        await asyncio.wait([user.on_update_state(self) for user in self._users], return_when=asyncio.ALL_COMPLETED)


b = Board()  # TODO: board by game_uid


async def user_ctl(websocket, path):
    print(path)  # TODO: FastAPI
    user = User(websocket, b)  # TODO: user_uid from Headers
    await user.serve()

start_server = websockets.serve(user_ctl, "0.0.0.0", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
