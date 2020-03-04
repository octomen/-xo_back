from collections import Counter
from itertools import chain
from enum import Enum
from typing import Optional


class SignEnum(Enum):
    X: str = 'x'
    O: str = 'o'
    N: str = 'n'


class User:
    def __init__(self, uid):
        self._uid = uid


class State:
    def __init__(self):
        self.board = [[SignEnum.N] * 3 for _ in range(3)]
        self.x_user: Optional[User] = None
        self.y_user: Optional[User] = None

    def is_connected(self, user_uid):
        return any(u and u.uid == user_uid for u in (self.x_user, self.y_user))

    def get_current_sign(self):
        counter = Counter(chain(*self.board))
        if counter.setdefault(SignEnum.X, 0) == counter.setdefault(SignEnum.O, 0):
            return SignEnum.X
        return SignEnum.O

    def add_user(self, user: User):
        
