# -*- coding: utf-8 -*-
from contextlib import ExitStack
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.actions import ERROR
from api.aioclub.action import Action
from api.controllers.chat import MESSAGE

CHAT_URL = '/chat/{chat}/{user}'


def test_send_message(client):
    chat = get_new_chat(client)

    with ExitStack() as stack:
        sockets: Dict[int, WebSocket]
        sockets = {
            i: stack.enter_context(client.websocket_connect(
                CHAT_URL.format(
                    chat=chat,
                    user=i,
                )
            ))
            for i in [1, 2, 3]
        }

        message = MESSAGE('hi! I\'m 1')
        sockets[1].send_text(message.to_json())

        for i in [2, 3]:
            receive_message = sockets[i].receive_json()
            assert message == Action.from_dict(receive_message)


def test_unregistered_chat(client):
    with ExitStack() as stack:
        socket: WebSocketTestSession
        socket = stack.enter_context(client.websocket_connect(
            CHAT_URL.format(
                chat=1,
                user=1,
            )
        ))
        data = socket.receive_json()
        data = Action.from_dict(data)
        assert data.action == ERROR
        with pytest.raises(WebSocketDisconnect):
            socket.receive_json()


def get_new_chat(client: TestClient):
    response = client.post("/chat")
    assert response.status_code == 200

    data = response.json()
    assert data['status'] == 'ok'
    return data['data']['uid']
