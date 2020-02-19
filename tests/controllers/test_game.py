# -*- coding: utf-8 -*-
import pytest

from api.controllers.game_controller import get_current_sign, X, O, N


@pytest.mark.parametrize('board, sign, desc', [
    ([[N, X, X], [N, O, O], [N, N, N]], X, 'X==O'),
    ([[N, X, X], [X, O, O], [N, N, N]], O, 'X>O'),
    ([[N, N, N], [N, N, N], [N, N, X]], O, 'one X'),
    ([[N, N, N], [N, N, N], [N, N, N]], X, 'first move'),
])
def test_get_current_sign(board, sign, desc):
    assert get_current_sign(board) == sign, desc
