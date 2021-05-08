#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
import re
from ..context import CONTEXT

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
    def empty(cls):
        return cls([])

    @classmethod
    def fromlist(cls, keys):
        return cls([ str(k) for k in keys])

    @classmethod
    def fromstring(cls, string):
        return cls(re.split(CONTEXT.path_split, string))

    def __init__(self, keys):
        self.keys = keys
        self.last = len(self.keys) - 1

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.keys == other.keys
        return False

    def __getitem__(self, n):
        return self.keys[n]

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        return CONTEXT.delimiter.join(map(str, self.keys))

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    def parent(self):
        return type(self)(self.keys[:-1])

    def subpath(self, key):
        return type(self)(self.keys + [ key ])
