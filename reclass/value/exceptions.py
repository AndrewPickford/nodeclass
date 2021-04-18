#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#

class ValueError(Exception):
    def __init__(self):
        super().__init__(value)
        self.value = value


class ValueRenderUndefinedError(ValueError):
    def __init__(self, value):
        super().__init__(value)


class MergeError(Exception):
    def __init__(self):
        super().__init__()


class MergeUndefinedError(MergeError):
    def __init__(self):
        super().__init__()


class MergeTypeError(MergeError):
    def __init__(self, first, second):
        super().__init__()
        self.first = first
        self.second = second
