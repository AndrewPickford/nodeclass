#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from ..exceptions import ReclassError
from ..utils.path import Path

class MergeError(ReclassError):
    def __init__(self, first, second):
        super().__init__()
        self.first = first
        self.second = second
        self.reverse_path = []


class MergeTypeError(MergeError):
    def __init__(self, first, second):
        super().__init__(first, second)

    @property
    def message(self):
        message = [ (0, 'Merge type error at: {0}'.format(Path.fromlist(self.reverse_path[::-1]))),
                    (2, self.first.url),
                    (2, self.second.url) ]
        return message


class MergeOverImmutableError(MergeError):
    def __init__(self, first, second):
        super().__init__(first, second)


class FrozenError(Exception):
    def __init__(self, url):
        super().__init__()
        self.url = url
