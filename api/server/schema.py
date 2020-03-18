# -*- coding: utf-8 -*-
import logging
from collections import defaultdict
from typing import Callable, Tuple, Dict, List

from api.server.action import Action, ActionType

logger = logging.getLogger(__name__)


class DefaultImplementation:
    pass


class EntityType:
    def __init__(self, name, scope):
        self.name = name
        self.scope = scope
        self.implementation = DefaultImplementation

    def __call__(self, implementation):
        self.implementation = implementation

    def create(self):
        entity = self.implementation()
        entity._self__type = self
        return entity


class Entity:
    def __init__(self, parent, pipe):
        self.__scope = None
        self.parent = parent
        self.pipe = pipe

    def emit(self, action: Action):
        pass


class MetaSchema(type):
    def __init__(cls, name, bases, dct):
        cls.subscribers = defaultdict(list)
        cls.entity_method_subscribers = defaultdict(list)
        cls.implementation = DefaultImplementation
        cls.entity_types = {}

        print(dct)
        for k, v in dct.get('__annotations__', {}).items():
            if v == EntityType:
                v = EntityType(k.lower(), cls)
                cls.entity_types[k.lower()] = v
                setattr(cls, k, v)
        super().__init__(name, bases, dct)


class Schema(metaclass=MetaSchema):
    def __init__(self, implementation):
        self.__class__.implementation = implementation

    @classmethod
    def get_route(cls):
        return cls.__name__.lower()

    @classmethod
    def create(cls):
        return cls.implementation()

    @classmethod
    def create_entity(cls, entity_type):
        entity_type = entity_type.lower()
        print(cls.entity_types)
        if entity_type not in cls.entity_types:
            raise Exception(f'there is not entity {entity_type} in schema {cls.__name__}')

        entity_type = cls.entity_types[entity_type]
        return entity_type.create()

    # @classmethod
    # def handle(cls, emitter, entity_type, action):



def METHOD(entity: EntityType, actions):
    if isinstance(actions, Action):
        actions = [actions]

    def _wrapper(func):
        for action in actions:
            observe_key = (entity, action.type_)
            entity.scope.entity_method_subscribers[observe_key].append(func)
            func.__dict__.setdefault('__actions', []).append((entity, action))
        return func
    return _wrapper


def BIND(entity: EntityType, actions) -> Callable:
    if isinstance(actions, Action):
        actions = [actions]

    def _wrapper(func):
        for action in actions:
            observe_key = (entity, action.type_)
            entity.scope.subscribers[observe_key].append(func)
        return func
    return _wrapper


class EmitKey:
    def __init__(self, entity_type: EntityType, action_type: ActionType):
        self.entity_type = entity_type
        self.action_type = action_type


class EmitData:
    def __init__(self, emitter, entity_type: EntityType, action: Action):
        self.emitter = emitter
        self.entity_type = entity_type
        self.action = action

    def is_(self, emit_key: EmitKey):
        return self.entity_type == emit_key.entity_type and self.action.type_ == emit_key.action_type

    def get_key(self):
        return EmitKey(self.entity_type, self.action.type_)

    def with_entity_template(self, entity_type: EntityType):
        return EmitData(entity_type, self.action)
