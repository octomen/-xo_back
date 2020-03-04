class DataSource:

    def __init__(self):
        from api.modules.state import State
        self.STORAGE = {'123': State()}

    def get(self, key):
        if key not in self.STORAGE:
            self.STORAGE[key] = {}
        return self.STORAGE[key]

    def set(self, key, value):
        self.STORAGE[key] = value
