# -*- coding: utf-8 -*-
import json
import time


class ActionType:
    def __init__(self, type_):
        self.type_ = type_

    def __repr__(self):
        return self.type_

    def __eq__(self, other):
        return self.type_ == other.self

    def __call__(self, payload):
        return Action(self, payload)


class Action:
    def __init__(self, action_type: ActionType, payload):
        self.type_ = action_type
        self.ts = int(time.time())
        self.payload = payload

    def to_json(self):
        return json.dumps(dict(
            type=str(self.type_),
            ts=self.ts,
            payload=self.payload,
        ))

    @classmethod
    def from_json(cls, message):
        message = json.dumps(message)
        type_ = message.pop('type')
        return cls(type_, message)


MESSAGE = ActionType('MESSAGE')
CREATE = ActionType('CREATE')
