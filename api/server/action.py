# -*- coding: utf-8 -*-
import json
import time


class ActionType:
    def __init__(self, type_):
        self.type_ = type_

    def __repr__(self):
        return self.type_


class Action:
    def __init__(self, action_type: ActionType, payload):
        self.type_ = action_type
        self.ts = int(time.time())
        self.payload = payload

    def serialize(self):
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


class EmitKey:
    def __init__(self, pipe_type: str, action_type: ActionType):
        self.pipe_type = pipe_type
        self.action_type = action_type


class EmitData:
    def __init__(self, pipe_type: str, action: Action):
        self.pipe_type = pipe_type
        self.action = action

    def is_(self, emit_key: EmitKey):
        return self.pipe_type == emit_key.pipe_type and self.action.type_ == emit_key.action_type

    def get_key(self):
        return EmitKey(self.pipe_type, self.action.type_)

    def with_pipe_type(self, pipe_type: str):
        return EmitData(pipe_type, self.action)


MESSAGE = ActionType('MESSAGE')
CREATE = ActionType('CREATE')
