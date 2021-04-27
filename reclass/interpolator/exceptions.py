#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#

class InterpolationError(Exception):
    def __init__(self):
        super().__init__()


class InterpolationExcessiveRevisitsError(InterpolationError):
    def __init__(self):
        super().__init__()


class InterpolationCircularReferenceError(InterpolationError):
    def __init__(self, path, reference):
        super().__init__()
        self.path = path
        self.reference = reference
