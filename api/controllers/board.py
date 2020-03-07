import asyncio
import logging
from typing import Callable

log = logging.getLogger(__name__)


class SignEnum:
    X: str = 'x'
    O: str = 'o'
    N: str = 'n'


class Board:
    TIE = 'TIE'
    POSITIVE = 'POS'

    def __init__(self):
        self._board = [[SignEnum.N] * 3 for _ in range(3)]
        self._on_state_change = []
        self._on_game_over = []
        self._movement_cnt = 0

    async def move(self, sign, point: tuple):
        log.debug('Move: {} {}'.format(point, sign))
        if self.is_occupied(point) or self.current_sign() is not sign:
            return  # TODO: raise "wrong move" client error
        self._board[point[0]][point[1]] = sign
        self._movement_cnt += 1
        if self._movement_cnt > 8:
            await asyncio.wait([c(self, sign, self.TIE) for c in self._on_game_over])
        if self._is_game_over(sign):
            await asyncio.wait([c(self, sign, self.POSITIVE) for c in self._on_game_over])

        await asyncio.wait([c(self) for c in self._on_state_change])

    def _is_game_over(self, sign):
        win_variations = [(0, 4, 8), (2, 4, 6), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 1, 2), (3, 4, 5), (6, 7, 8)]
        for v in win_variations:
            if all(self._board[p // 3][p % 3] is sign for p in v):
                return True
        return False

    def on_game_over(self, callback: Callable):
        self._on_game_over.append(callback)

    def is_occupied(self, point: tuple):
        return self._board[point[0]][point[1]] != SignEnum.N

    def current_sign(self):
        return SignEnum.X if self._movement_cnt % 2 == 0 else SignEnum.O

    def on_state_change(self, callback: Callable):
        self._on_state_change.append(callback)

    def get_state(self):
        return self._board
