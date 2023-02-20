#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from ..exceptions import InterpolationError, ProcessError
from ..utils.path import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any
    from ..exceptions import MessageList
    from ..utils.url import Url
    from .dictionary import Dictionary
    from .value import Value
    from .vlist import VList


class MergeError(InterpolationError):
    def __init__(self, first: 'Value', second: 'Value'):
        super().__init__()
        self.first = first
        self.second = second


class MergeIncompatibleTypes(MergeError):
    def __init__(self, first: 'Value', second: 'Value'):
        super().__init__(first, second)

    def msg(self) -> 'MessageList':
        path = Path.fromstring(self.category) + self.path
        return [ 'Incompatible merge types at {0}, in:'.format(path), 2,
                 self.first.url,
                 self.second.url ]


class MergeOverImmutable(MergeError):
    def __init__(self, first: 'Value', second: 'Value', path: 'Path'):
        super().__init__(first, second)
        self.reverse_path.append(path)

    def msg(self) -> 'MessageList':
        path = Path.fromstring(self.category) + self.path
        return [ 'Merge over immutable at {0} in:'.format(path), 2,
                 self.first.url,
                 self.second.url ]


class ValueError(InterpolationError):
    def __init__(self, value: 'Value'):
        super().__init__()
        self.value = value


class DictionaryResolve(ValueError):
    def __init__(self, value: 'Dictionary'):
        super().__init__(value)

    def msg(self) -> 'MessageList':
        return [ 'Internal error: Dictionary reached resolve' ] + \
               self.traceback()


class ListResolve(ValueError):
    def __init__(self, value: 'VList'):
        super().__init__(value)

    def msg(self) -> 'MessageList':
        return [ 'Internal error: List reached resolve' ] + \
               self.traceback()


class FrozenHierarchy(ProcessError):
    def __init__(self, url: 'Url', category: 'str'):
        super().__init__()
        self.url = url
        self.category = category

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Internal error: attempt to change frozen hierarchy',
                 'url: {0}'.format(self.url) ] + \
               self.traceback()


class NotHierarchy(ProcessError):
    def __init__(self, url: 'Url', category: 'str', other: 'Any'):
        super().__init__()
        self.url = url
        self.category = category
        self.other = other

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Internal error: attempt to merge non hierarchy object',
                 'url: {0}'.format(self.url),
                 'other type: {0}'.format(type(self.other)) ] + \
               self.traceback()


class NoSuchPath(Exception):
    def __init__(self, missing_path: 'Path'):
        super().__init__()
        self.missing_path = missing_path
