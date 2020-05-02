import logging
from typing import List, Optional, Set

from api.aioclub.action import ActionType, Action
from api.modules.main import storage
from . import Board, SignEnum, User
from .board import STATE_CHANGE, GAME_OVER
from ..actions import DISCONNECT
from ..aioclub.room import Room

log = logging.getLogger(__name__)

STATE = ActionType('STATE')
MOVE = ActionType('MOVE')


class Game:
    def __init__(self, room: Room):
        self.room = room
        self._gamer_count = 2
        self._gamers: List[Optional[User]] = [None] * self._gamer_count
        self._gamer_bind = {}
        self._watchers: Set[User] = set()
        self._board: Board = Board(self.room)
        self.room.subscribe(self._board, STATE_CHANGE, self.state_notify)
        self.room.subscribe(self._board, GAME_OVER, self.on_game_over)

    async def add_gamer(self, user: User):
        self._add_gamer(user)
        await self.state_notify()

    def _add_gamer(self, user: User):
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
        self.room.subscribe(user, MOVE, self.on_user_action)

    def add_watcher(self, user: User):
        self._watchers.add(user)
        self.room.subscribe(user, DISCONNECT, self.disconnect_user)

    async def disconnect_user(self, user: User, _=None):
        try:
            self._watchers.remove(user)
            self._gamers[self._gamers.index(user)] = None
        except ValueError:
            pass

    async def on_user_action(self, user: User, action: Action):
        point = action.payload['point']
        await self._board.move(
            SignEnum.X if self._gamers.index(user) == 0 else SignEnum.O,
            point,
        )

    async def state_notify(self, _board=None, _action=None):
        state = STATE(self._board.get_state())
        for u in self._watchers:
            await u.send(state)

    async def on_game_over(self, board: Board, action: Action):
        sign = action.payload['sign']
        result = action.payload['result']

        action = GAME_OVER({
            'winner': sign if result.payload is board.POSITIVE else 'nobody'
        })
        for u in self._watchers:
            await u.send(action)


def get_or_create(game_uid: str) -> Game:
    game = storage.get(game_uid)
    if not game:
        return storage.set(game_uid, Game())
    return game
