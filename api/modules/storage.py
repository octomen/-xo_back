class DataSource:

    def __init__(self):
        self.STORAGE = {}

    def get(self, key):
        return self.STORAGE.get(key)

    def set(self, key, value):
        self.STORAGE[key] = value
