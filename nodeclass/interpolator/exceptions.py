#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from ..exceptions import InterpolationError
from ..utils.path import Path

class MergableInterpolationError(InterpolationError):
    pass


class NoSuchReference(MergableInterpolationError):
    def __init__(self, url, path, reference, hierarchy_type=None):
        super().__init__()
        self.url = url
        self.path = path
        self.reference = reference
        self.hierarchy_type = hierarchy_type

    def msg(self):
        path = Path.fromstring(self.hierarchy_type) + self.path
        return [ 'Cannot resolve {0}, at {1}, in {2}'.format(self.reference.as_ref(), path, self.url) ]


class ExcessivePathRevisits(MergableInterpolationError):
    def __init__(self, url, path, hierarchy_type=None):
        super().__init__()
        self.url = url
        self.path = path
        self.hierarchy_type = hierarchy_type

    def msg(self):
        path = Path.fromstring(self.hierarchy_type) + self.path
        return [ 'Too many path revisits during interpolation at {0}, in {1}'.format(path, self.url) ]


class CircularReference(MergableInterpolationError):
    def __init__(self, url, path, reference):
        super().__init__()
        self.url = url
        self.path = path
        self.reference = reference

    def msg(self):
        path = Path.fromstring(self.hierarchy_type) + self.path
        return [ 'Circular reference {0}, at {1}, in {2}'.format(self.reference.as_ref(), path, self.url) ]


class MultipleInterpolationErrors(InterpolationError):
    def __init__(self, exceptions):
        super().__init__()
        self.exceptions = exceptions

    def message(self):
        msg = []
        for exception in self.exceptions:
            msg.extend(exception.msg())
        return super().message() + msg


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
               [ 'url: {0}'.format(self.url),
                 'hierarchy: {0}'.format(self.hierarchy_type),
                 'path: {0}'.format(self.path),
                 'value: {0}'.format(self.value),
                 'unhandled error during interpolation:',
                 2,
                 str(repr(self.exception)) ] + \
               self.traceback() +\
               self.traceback_other(self.exception)


class InventoryQueryError(InterpolationError):
    def __init__(self, query, exception):
        super().__init__()
        self.query = query
        self.exception = exception
        self.path = None
        self.url = None

    def message(self):
        path = Path.fromstring(self.hierarchy_type) + self.path
        return super().message() + \
               [ 'Failed inv query: {0}'.format(str(self.query)),
                 'at {0}, in {1}'.format(path, self.url) ] + \
               self.exception.message()
