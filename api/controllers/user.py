import logging
import hashlib

from api.aioclub.action import Action
from api.aioclub.bots import Bot

log = logging.getLogger(__name__)


class User:
    def __init__(self, uid: str, bot: Bot):
        self.uid = uid
        self.bot = bot

    def __eq__(self, other):
        if not hasattr(other, 'uid'):
            return False
        return other.uid == self.uid

    def __hash__(self):
        return int(hashlib.sha1(self.uid.encode()).hexdigest(), 16)

    async def send(self, data: Action):
        await self.bot.send(data)
