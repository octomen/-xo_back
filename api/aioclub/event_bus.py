# -*- coding: utf-8 -*-
import asyncio
import logging
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from typing import Awaitable, Callable, Dict, Hashable, Set, Any

from api.aioclub.action import ActionType, Action


logger = logging.getLogger(__name__)

# TODO: попробовать добавить возможность скормить синхронную функцию
Subscriber = Callable[[Any, Action], Awaitable]


class IEventBus(ABC):
    @abstractmethod
    async def run(self):
        pass

    @abstractmethod
    async def cancel(self):
        pass

    @abstractmethod
    async def emit(self, emitter: Hashable, data: Action):
        pass

    @abstractmethod
    def subscribe(self, emitter: Hashable, action: ActionType, subscriber: Subscriber):
        pass

    @abstractmethod
    def unsubscribe(self, emitter: Hashable, action: ActionType, subscriber: Subscriber):
        pass


class EventBus(IEventBus):
    _subscriptions: Dict[Hashable, Dict[ActionType, Set[Subscriber]]]

    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self._task_generator = loop or asyncio
        self._tasks = deque()
        self._is_working = False
        self._cleaner = None
        # TODO: weakref
        self._subscriptions = defaultdict(lambda: defaultdict(set))

    async def join_until_empty(self):
        while self._tasks:
            await asyncio.sleep(0.01)

    def run(self):
        self._is_working = True
        self._cleaner = self._task_generator.create_task(self._task_cleaner())

    def cancel(self):
        self._is_working = False
        while self._tasks:
            self._tasks.popleft().cancel()
        if self._cleaner:
            self._cleaner.cancel()

    async def emit(self, emitter: Hashable, data: Action):
        logger.debug('emit data=%s by %s', data, emitter)
        if not self._is_working:
            return

        if emitter not in self._subscriptions:
            return

        action = data.action
        if action not in self._subscriptions[emitter]:
            return

        for subscriber in self._subscriptions[emitter][action]:
            logger.debug('subscriber %s received data', subscriber)
            self._tasks.append(self._task_generator.create_task(subscriber(emitter, data)))
        await asyncio.sleep(0)

    def subscribe(self, emitter: Hashable, action: ActionType, subscriber: Subscriber):
        logger.debug('add subscriber(%s) to emitter(%s action=%s)', subscriber.__name__, emitter, action)
        self._subscriptions[emitter][action].add(subscriber)

    def unsubscribe(self, emitter: Hashable, action: ActionType, subscriber: Subscriber):
        if not self.is_subscribed(emitter, action, subscriber):
            logger.warning(f'emitter({emitter} action={action}) '
                           f'does not have such subscriber(name={subscriber.__name__})')
            return

        self._subscriptions[emitter][action].remove(subscriber)
        self._clear(emitter, action)

    def is_subscribed(self, emitter: Hashable, action: ActionType, subscriber: Subscriber):
        if emitter not in self._subscriptions:
            return False
        if action not in self._subscriptions[emitter]:
            return False
        return subscriber in self._subscriptions[emitter][action]

    def _clear(self, emitter: Hashable, action: ActionType):
        if not self._subscriptions[emitter][action]:
            del self._subscriptions[emitter][action]
        if not self._subscriptions[emitter]:
            del self._subscriptions[emitter]

    async def _task_cleaner(self):
        while self._is_working:
            if self._tasks:
                task = self._tasks.popleft()
                if task.done():
                    continue
                self._tasks.append(task)
            await asyncio.sleep(0.1)
