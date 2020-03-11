# -*- coding: utf-8 -*-
import logging
from abc import abstractmethod
from typing import Callable, Tuple, Dict, List

from api.server.action import Action
from api.server.pipe import Pipe, PipeType, EmitKey

logger = logging.getLogger(__name__)


class Entity:
    def __init__(self):
        self._class = None

    def emit(self, action):
        pass

    def __call__(self, _class):
        self._class = _class


class ISchema:
    @abstractmethod
    def get_route(self):
        return self.__class__.__name__.lower()

    @abstractmethod
    def create_entity(self, pipe_type: PipeType,  pipe: Pipe) -> Dict[EmitKey, List[Pipe]]:
        pass


class Schema:
    def __init__(self):
        self.name2entities = {
            k.lower(): v for k, v
            in self.__class__.__dict__.items()
            if isinstance(v, Entity)
        }
        self.entities2name = {v: k for k, v in self.name2entities.items()}

        self._entry_point = None
        self._entity_factory = {}
        self._subscribers = {}

    def get_entity_name(self, entity: Entity):
        return

    def create_entity(self, pipe: Pipe):
        pass

    def ENTRYPOINT(self, _class):
        self._entry_point = _class
        return _class

    def CREATE(self, entity_name: Entity) -> Callable:
        if entity_name not in self.entities2name:
            raise Exception(f'Such entity did not register in schema {self.__class__.__name__}')
        logger.info(f'create entity fabric for {self.entities2name[entity_name]}')

        def _wrapper(func):
            self._entity_factory[entity_name] = func.__name__
            return func
        return _wrapper

    def METHOD(self, entity: Entity, actions):
        if isinstance(actions, Action):
            actions = [actions]

        def _wrapper(func):
            for action in actions:
                func.__dict__.setdefault('__actions', []).append((entity, action))
            return func
        return _wrapper

    def BIND(self, entity: Entity, actions) -> Callable:
        if isinstance(actions, Action):
            actions = [actions]

        def _wrapper(func):
            for action in actions:
                self._subscribers.setdefault((entity, action.type_), []).append(func)
            return func
        return _wrapper

    def process_entity(self, type_: str, pipe):
        entity_type = self.name2entities.get(type_)
        if entity_type in self._entity_factory:
            entity = self._entity_factory[entity_type]
            entity.entity = pipe
            return entity
        else:
            return pipe
