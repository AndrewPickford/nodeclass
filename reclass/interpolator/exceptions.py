#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#

class InteroplationError(Exception):
    def __init__(self):
        super().__init__()


class InteroplationInfiniteRecursionError(InteroplationError):
    def __init__(self):
        super().__init__()
