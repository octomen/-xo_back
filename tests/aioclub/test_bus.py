# -*- coding: utf-8 -*-
import asyncio

import pytest

from api.aioclub.action import ActionType
from api.aioclub.event_bus import EventBus

SAY = ActionType('SAY')


class EmitterForTest:
    def __init__(self, bus, delay, counter_name):
        self.bus = bus
        self.delay = delay
        self.counter_name = counter_name

    async def say(self, _, data):
        data.payload[self.counter_name] -= 1
        data.payload['log'].append(self.counter_name)
        await asyncio.sleep(self.delay)
        if data.payload[self.counter_name] > 0:
            await self.bus.emit(self, SAY(data.payload))


class TestBus:

    def set_up(self, bus):
        self.emitter1 = EmitterForTest(bus, 0.05, 'count1')
        self.emitter2 = EmitterForTest(bus, 0.08, 'count2')

        self.payload = dict(count1=2, count2=3, log=[])

    async def emit(self, bus):
        await bus.emit(self.emitter1, SAY(self.payload))
        await bus.emit(self.emitter2, SAY(self.payload))

    @pytest.mark.asyncio
    async def test_right_cross_messaging(self, bus: EventBus):
        self.set_up(bus)
        bus.subscribe(self.emitter1, SAY, self.emitter2.say)
        bus.subscribe(self.emitter2, SAY, self.emitter1.say)

        await self.emit(bus)
        await bus.join_until_empty()

        assert self.payload == dict(
            count1=-1,
            count2=1,
            log=['count2', 'count1', 'count2', 'count1', 'count1'],
        )

    @pytest.mark.asyncio
    async def test_right_messaging(self, bus: EventBus):
        self.set_up(bus)
        bus.subscribe(self.emitter1, SAY, self.emitter1.say)
        bus.subscribe(self.emitter2, SAY, self.emitter2.say)

        await self.emit(bus)
        await bus.join_until_empty()

        assert self.payload == dict(
            count1=0,
            count2=0,
            log=['count1', 'count2', 'count1', 'count2', 'count2'],
        )
