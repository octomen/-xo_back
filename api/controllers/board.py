import logging

from api.aioclub.action import ActionType
from api.aioclub.room import Room

log = logging.getLogger(__name__)
GAME_OVER = ActionType('GAME_OVER')
STATE_CHANGE = ActionType('STATE_CHANGE')


class SignEnum:
    X: str = 'x'
    O: str = 'o'
    N: str = 'n'


class Board:
    TIE = 'TIE'
    POSITIVE = 'POS'

    def __init__(self, room: Room):
        self.room = room
        self._board = [[SignEnum.N] * 3 for _ in range(3)]
        self._movement_cnt = 0

    async def move(self, sign, point: tuple):
        log.debug('Move: {} {}'.format(point, sign))
        if self.is_occupied(point) or self.current_sign() is not sign:
            return  # TODO: raise "wrong move" client error
        self._board[point[0]][point[1]] = sign
        self._movement_cnt += 1
        if self._movement_cnt > 8:
            await self.game_over(sign, self.TIE)
        if self._is_winner(sign):
            await self.game_over(sign, self.POSITIVE)

        await self.room.emit(self, STATE_CHANGE({}))

    async def game_over(self, sign, result):
        await self.room.emit(self, GAME_OVER({
            'sign': sign,
            'result': result,
        }))

    def _is_winner(self, sign):
        win_variations = [(0, 4, 8), (2, 4, 6), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 1, 2), (3, 4, 5), (6, 7, 8)]
        for v in win_variations:
            if all(self._board[p // 3][p % 3] is sign for p in v):
                return True
        return False

    def is_occupied(self, point: tuple):
        return self._board[point[0]][point[1]] != SignEnum.N

    def current_sign(self):
        return SignEnum.X if self._movement_cnt % 2 == 0 else SignEnum.O

    def get_state(self):
        return self._board
