#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from __future__ import annotations
from typing import TYPE_CHECKING

import re
from ..context import CONTEXT

if TYPE_CHECKING:
    from typing import Any


class Path:
    ''' Represent a path into a nested dictionary.
    Create using factory functions:

    >>> path = Path.empty()
    >>> str(path)
    ''

    >>> path = Path.fromstring('foo:bar')
    >>> str(path)
    'foo:bar'

    >>> path = Path.fromlist(['foo', 'bar'])
    >>> str(path)
    'foo:bar'
    '''

    __slots__ = ('keys', 'last')

    @classmethod
    def empty(cls) -> Path:
        return cls([])

    @classmethod
    def fromlist(cls, keys: list[Any]) -> Path:
        return cls([ str(k) for k in keys])

    @classmethod
    def fromstring(cls, string: str) -> Path:
        return cls(re.split(CONTEXT.path_split, string))

    def __init__(self, keys: list[str]):
        self.keys = keys
        self.last = len(self.keys) - 1

    def __add__(self, other: Path) -> Path:
        return type(self)(self.keys + other.keys)

    def __eq__(self, other: Any) -> bool:
        if self.__class__ == other.__class__:
            return self.keys == other.keys
        return False

    def __getitem__(self, n: int) -> str:
        return self.keys[n]

    def __hash__(self) -> int:
        return hash(self.__str__())

    def __str__(self) -> str:
        return CONTEXT.delimiter.join(map(str, self.keys))

    def __repr__(self) -> str:
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    def as_ref(self) -> str:
        return str(self).join(CONTEXT.settings.reference_sentinels)

    def parent(self) -> Path:
        return type(self)(self.keys[:-1])

    def subpath(self, key: Any) -> Path:
        return type(self)(self.keys + [ str(key) ])
