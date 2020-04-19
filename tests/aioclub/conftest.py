# -*- coding: utf-8 -*-
import pytest

from api.aioclub.event_bus import EventBus
from api.aioclub.room import Room


@pytest.fixture()
def bus(event_loop) -> EventBus:
    _bus = EventBus(loop=event_loop)
    _bus.run()
    yield _bus
    _bus.cancel()


@pytest.fixture()
def room(event_loop, bus):
    return Room(event_loop, bus)
