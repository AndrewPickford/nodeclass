#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
import re
from reclass.settings import defaults


class Path:
    '''
    Represents a path into a nested dictionary.
    Should not be created directly instead use the factory functions:


    path = Path.Empty()
    path = Path.FromList([ 'foo', 'bar' ])
    path = Path.FromString('foo:bar')
    '''

    @classmethod
    def empty(cls):
        return cls([])

    @classmethod
    def fromlist(cls, keys):
        return cls(map(str, path))

    @classmethod
    def fromstring(cls, string, path_split):
        return cls(re.split(path_split, string))

    def __init__(self, keys):
        self._keys = keys
        self._hash = hash(str(self))
        self.last = len(self._keys) - 1

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
        return self.string(defaults.delimiter)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    def string(self, delimiter):
        return delimiter.join(map(str, self._keys))

    def subpath(self, key):
        return Path(self._keys + [ key ])
