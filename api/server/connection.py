# -*- coding: utf-8 -*-
class ConnectionInfo:
    def __init__(self, websocket, path: str):
        self.websocket = websocket
        self.path = path
        self.splitted_path = self.path.split('/')[1:]

    def get_process_type(self):
        return self.splitted_path[0]

    def get_process_key(self):
        return tuple(self.splitted_path[:2])

    def get_entity_type(self):
        return self.splitted_path[2]
