import asyncio
import logging
from typing import List, Optional, Set

from api.modules.main import storage
from . import Board, SignEnum, User

log = logging.getLogger(__name__)


class Game:
    def __init__(self):
        self._gamer_count = 2
        self._gamers: List[Optional[User]] = [None] * self._gamer_count
        self._gamer_bind = {}
        self._watchers: Set[User] = set()
        self._board: Board = Board()
        self._board.on_state_change(self.state_notify)

    # async def add_gamer(self, user: User):
    #     await user.send('Connecting ...')
    #     self._add_gamer(user)

    def add_gamer(self, user: User):
        log.debug(self._gamers)

        if user in self._gamers:
            return

        if all(self._gamers):
            raise Exception

        self.add_watcher(user)
        if user.uid not in self._gamer_bind:
            if len(self._gamer_bind) >= self._gamer_count:
                raise Exception
            start = self._gamers.index(None)
            while True:
                if start not in self._gamer_bind.values():
                    self._gamer_bind[user.uid] = start
                    break
                start = self._gamers.index(None, start)
        self._gamers[self._gamer_bind[user.uid]] = user
        user.on_action(self.on_user_action)

    def add_watcher(self, user: User):
        self._watchers.add(user)
        user.on_disconnect(self.disconnect_user)

    def kick_user(self, user: User):
        self._gamer_bind.pop(user.uid)
        self.disconnect_user(user)

    def disconnect_user(self, user: User):
        try:
            self._watchers.remove(user)
            self._gamers[self._gamers.index(user)] = None
        except ValueError:
            pass

    async def on_user_action(self, user: User, data: tuple):
        await self._board.move(SignEnum.X if self._gamers.index(user) == 0 else SignEnum.O, data)

    async def state_notify(self, board: Board):
        await asyncio.wait([u.send(board.get_state()) for u in self._watchers])  # TODO: serialize board state


def get_or_create(game_uid: str) -> Game:
    game = storage.get(game_uid)
    if not game:
        return storage.set(game_uid, Game())
    return game
