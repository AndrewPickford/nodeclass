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

    Path.FromList([ 'foo', 'bar' ])
    Path.FromString('foo:bar')
    '''

    @classmethod
    def FromList(cls, parts):
        return cls(map(str, path))

    @classmethod
    def FromString(cls, string):
        return cls(re.split(SETTINGS.path_split, string))

    def __init__(self, parts=[]):
        self._parts = parts

    def __eq__(self, other):
        if not (isinstance(other, self.__class__)):
            return False
        return self._parts == other._parts

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return SETTINGS.delimiter.join(map(str, self._parts))

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, str(self))
