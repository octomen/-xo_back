# -*- coding: utf-8 -*-
import json
import time

from api.aioclub.exceptions import MessageParseException


class ActionType:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, ActionType):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __call__(self, payload):
        return Action(self, payload)


class Action:
    def __init__(self, action: ActionType, payload, ts=None):
        self.action = action
        self.ts = ts or int(time.time())
        self.payload = payload

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return dict(
            type=str(self.action),
            ts=self.ts,
            payload=self.payload,
        )

    @classmethod
    def from_json(cls, message):
        try:
            message = json.loads(message)
            return cls.from_dict(message)
        except Exception as e:
            raise MessageParseException(str(e))

    @classmethod
    def from_dict(cls, data):
        try:
            return cls(
                    action=ActionType(data['type']),
                    payload=data['payload'],
                    ts=data.get('ts'),

                )
        except KeyError as e:
            raise MessageParseException(str(e))

    def __repr__(self):
        return f'<ActionData action={self.action} ts={self.ts} payload={self.payload}>'

    def __eq__(self, other):
        if not isinstance(other, Action):
            return False
        return self.to_dict() == other.to_dict()
