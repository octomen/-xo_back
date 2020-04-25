# -*- coding: utf-8 -*-
import pytest
from starlette.testclient import TestClient

from api.aioclub.event_bus import EventBus
from api.aioclub.room import Room
from api.app import create_app


@pytest.fixture()
def bus(event_loop) -> EventBus:
    _bus = EventBus(event_loop)
    _bus.run()
    yield _bus
    _bus.cancel()


@pytest.fixture()
def room(bus):
    return Room(bus)


@pytest.fixture()
def client():
    with TestClient(create_app()) as client:
        yield client
