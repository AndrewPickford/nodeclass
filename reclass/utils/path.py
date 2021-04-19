#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
import re

from reclass.settings import SETTINGS


class Path:
    '''
    Represents a path into a nested dictionary.

    Should not be created directly instead use the generator functions:

    path = Path.Empty()
    path = Path.FromList([ 'foo', 'bar' ])
    path = Path.FromString('foo:bar')
    '''

    @classmethod
    def Empty(cls):
        return cls([])

    @classmethod
    def FromList(cls, keys):
        return cls(map(str, path))

    @classmethod
    def FromString(cls, string):
        return cls(re.split(SETTINGS.path_split, string))

    def __init__(self, keys):
        self._keys = keys
        self._hash = hash(''.join(map(str, self._keys)))

    def __eq__(self, other):
        if self._hash != self._hash:
            return False
        return self._keys == other._keys

    def __getitem__(self, n):
        return self._keys[n]

    def __ne__(self, other):
        if self._hash != self._hash:
            return True
        return self._keys != other._keys

    def __hash__(self):
        return self._hash

    def __str__(self):
        return SETTINGS.delimiter.join(map(str, self._keys))

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    def subpath(self, key):
        return Path(self._keys + [ key ])
