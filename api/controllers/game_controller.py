from uuid import uuid4
from api.modules.main import storage


def get_state(game_uid: str):
    return storage.get(game_uid)


def create():
    game_uid = str(uuid4())
    storage.set(game_uid, {'board': [[None] * 3 for _ in range(3)], 'x': str(uuid4()), 'o': str(uuid4())})
    return get_state(game_uid)


def move(game_uid: str, user_uid: str, point: tuple):
    game = storage.get(game_uid)
    board = game['board']
    sign = 'x' if user_uid == game['x'] else 'o'
    x_point, y_point = point

    if board[x_point][y_point] is not None:
        raise Exception('Error!')

    # TODO: check is my move ?
    board[x_point][y_point] = sign
    return get_state(game_uid)
