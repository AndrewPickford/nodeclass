#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from ..exceptions import InterpolationError


class NoSuchReference(InterpolationError):
    def __init__(self, url, path, reference):
        super().__init__()
        self.url = url
        self.path = path
        self.reference = reference

    def message(self):
        return super().message() + \
               [ 'No such reference: {0}'.format(self.reference) ]


class ExcessivePathRevisits(InterpolationError):
    def __init__(self, url, path):
        super().__init__()
        self.url = url
        self.path = path

    def message(self):
        return super().message() + \
               [ 'Internal error: Too many path revisits during interpolation' ] + \
               self.traceback()


class CircularReference(InterpolationError):
    def __init__(self, url, path, reference):
        super().__init__()
        self.url = url
        self.path = path
        self.reference = reference

    def message(self):
        return super().message() + \
               [ 'Circular reference: {0}'.format(self.reference) ]


class InterpolateUnhandledError(InterpolationError):
    def __init__(self, exception, node=None, url=None, hierarchy_type=None, path=None, value=None):
        super().__init__()
        self.exception = exception
        self.node = node
        self.url = url
        self.hierarchy_type = hierarchy_type
        self.path = path
        self.value = value

    def message(self):
        return super().message() + \
               [ 'Unhandled error during interpolation',
                 'Value: {0}'.format(self.value),
                 str(repr(self.exception)) ] + \
               self.traceback() +\
               self.traceback_other(self.exception)
