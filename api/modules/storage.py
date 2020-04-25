import uuid


class DataSource:

    def __init__(self):
        self.STORAGE = {}

    def get(self, key):
        if key not in self.STORAGE:
            self.STORAGE[key] = {}
        return self.STORAGE[key]

    def set(self, key, value):
        self.STORAGE[key] = value
        return value
