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
    state.add_user(User(user_uid))
    return state


def move(game_uid: str, user_uid: str, point: tuple):
    state = get_state(game_uid)
    state.move(User(user_uid), point)
    return state
