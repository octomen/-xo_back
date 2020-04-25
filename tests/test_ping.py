# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient

from api.app import app


def test_ping():
    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'data': 'pong',
    }
