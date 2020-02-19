from collections import Counter
from itertools import chain
from typing import List
from uuid import uuid4
from api.modules.main import storage

X: str = 'x'
O: str = 'o'
N = None


def get_state(game_uid: str):
    return storage.get(game_uid)


def create():
    game_uid = str(uuid4())
    storage.set(game_uid, {'board': [[N] * 3 for _ in range(3)], X: str(uuid4()), O: str(uuid4())})
    return get_state(game_uid)


def move(game_uid: str, user_uid: str, point: tuple):
    game = storage.get(game_uid)
    board = game['board']
    sign = X if user_uid == game[X] else O
    x_point, y_point = point

    if board[x_point][y_point] is not None:
        raise Exception('Error!')

    if sign != get_current_sign(board):
        raise Exception('Other player move at this moment')

    board[x_point][y_point] = sign
    return get_state(game_uid)


def get_current_sign(board: List[List]) -> str:
    counter = Counter(chain(*board))
    if counter.setdefault(X, 0) == counter.setdefault(O, 0):
        return X
    return O
