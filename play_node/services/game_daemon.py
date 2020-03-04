# -*- coding: utf-8 -*-
import requests

from models.point import Point


class GameDaemon:
    def __init__(self, url):
        self._url = url

    def move(self, game: str, user: str, point: Point):
        requests.post('{url}/{}')
