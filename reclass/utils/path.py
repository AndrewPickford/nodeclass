#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
import re
from reclass.settings import defaults


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

    delimiter = defaults.delimiter
    path_split = r'(?<!\\)' + re.escape(defaults.delimiter)

    @classmethod
    def empty(cls):
        return cls([])

    @classmethod
    def fromlist(cls, keys):
        return cls([ str(k) for k in keys])

    @classmethod
    def fromstring(cls, string):
        return cls(re.split(cls.path_split, string))

    def __init__(self, keys):
        self.keys = keys
        self.last = len(self.keys) - 1
        self._hash = hash(str(self))

    def __eq__(self, other):
        if self._hash != self._hash:
            return False
        return self.keys == other.keys

    def __getitem__(self, n):
        return self.keys[n]

    def __ne__(self, other):
        if self._hash != self._hash:
            return True
        return self.keys != other.keys

    def __hash__(self):
        return self._hash

    def __str__(self):
        return self.delimiter.join(map(str, self.keys))

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    def parent(self):
        return type(self)(self.keys[:-1])

    def subpath(self, key):
        return type(self)(self.keys + [ key ])
