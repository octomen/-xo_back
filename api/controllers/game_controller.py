from typing import List
from uuid import uuid4
from api.modules.main import storage
from api.modules.state import State, User, SignEnum


def get_state(game_uid: str) -> State:
    return storage.get(game_uid)


def create():
    game_uid = str(uuid4())
    storage.set(game_uid, State())
    return get_state(game_uid)


def join(game_uid, user_uid):
    state = get_state(game_uid)

    if state.is_connected(user_uid):
        return state

    user = User(user_uid)
    if not state.x_user:
        state.x_user = user
    elif not state.y_user:
        state.y_user = user
    else:
        raise Exception()

    return state


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
