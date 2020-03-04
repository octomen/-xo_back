from collections import Counter
from itertools import chain
from enum import Enum
from typing import List, Optional


class SignEnum(Enum):
    X: str = 'x'
    O: str = 'o'
    N: str = 'n'


class User:
    def __init__(self, uid):
        self.uid = uid

    def __eq__(self, other: 'User'):
        return self.uid == other.uid


class State:
    def __init__(self):
        self.board = [[SignEnum.N] * 3 for _ in range(3)]
        self._users: List[User] = []
        self._count_users = 2

    def get_current_sign(self):
        counter = Counter(chain(*self.board))
        if counter.setdefault(SignEnum.X, 0) == counter.setdefault(SignEnum.O, 0):
            return SignEnum.X
        return SignEnum.O

    def add_user(self, user: User):
        if user in self._users:
            return

        if len(self._users) >= self._count_users:
            raise Exception()

        self._users.append(user)

    def current_user_uid(self) -> Optional[User]:
        if len(self._users) < self._count_users:
            return None
        counter = Counter(chain(*self.board))
        if counter.setdefault(SignEnum.X, 0) == counter.setdefault(SignEnum.O, 0):
            return self._users[0].uid
        return self._users[1].uid

    def move(self, user: User, point: tuple):
        sign = SignEnum.Y
        if user == self._users[0]:
            sign = SignEnum.X

        self.board[point[0]][point[1]] = sign
