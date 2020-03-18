import asyncio
import logging
from typing import Callable

log = logging.getLogger(__name__)


class SignEnum:
    X: str = 'x'
    O: str = 'o'
    N: str = 'n'


class Board:
    def __init__(self):
        self._board = [[SignEnum.N] * 3 for _ in range(3)]
        self._on_state_change = []

    async def move(self, sign, point: tuple):
        log.debug('Move: {} {}'.format(point, sign))
        self._board[point[0]][point[1]] = sign
        await asyncio.wait([c(self) for c in self._on_state_change])

    def on_state_change(self, callback: Callable):
        self._on_state_change.append(callback)

    def get_state(self):
        return self._board
