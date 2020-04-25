# -*- coding: utf-8 -*-
import asyncio
from abc import ABC, abstractmethod

from api.aioclub.action import Action


class Writer(ABC):
    @abstractmethod
    async def write(self, action: Action):
        pass


class Bot(ABC):
    def __init__(self):
        self._is_alive = True

    def kill(self):
        self._is_alive = False

    async def join(self):
        """Дождаться приема всех сообщений"""
        while self._is_alive:
            await asyncio.sleep(0.01)

    @abstractmethod
    async def receive(self, writer: Writer):
        """Потребляет сообщения из внешнего мира и пишет в шину"""

    @abstractmethod
    async def send(self, action: Action):
        """Отправляет сообщения во внешний мир"""
