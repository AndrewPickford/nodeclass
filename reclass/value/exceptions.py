#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#

class MergeError(Exception):
    def __init__(self):
        super().__init__()


class MergeTypeError(MergeError):
    def __init__(self, first, second):
        super().__init__()
        self.first = first
        self.second = second


class MergeOverImmutableError(MergeError):
    def __init__(self, first, second):
        super().__init__()
        self.first = first
        self.second = second


class FrozenError(Exception):
    def __init__(self, url):
        super().__init__()
        self.url = url
