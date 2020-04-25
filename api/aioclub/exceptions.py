# -*- coding: utf-8 -*-
class ProcessingException(Exception):
    pass


class MessageParseException(Exception):
    def __init__(self, parent_exc):
        self.parent_exc = parent_exc
