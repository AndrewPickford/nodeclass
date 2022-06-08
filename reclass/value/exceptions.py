#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from ..exceptions import ProcessError


class MergeError(ProcessError):
    def __init__(self, first, second):
        super().__init__()
        self.url = first.url
        self.first = first
        self.second = second

    def message(self):
        return super().message()


class MergeIncompatibleTypes(MergeError):
    def __init__(self, first, second):
        super().__init__(first, second)

    def message(self):
        return super().message() + \
               [ 'Incompatible merge types in: ',
                 self.first.url,
                 self.second.url ]


class MergeOverImmutable(MergeError):
    def __init__(self, first, second, path):
        super().__init__(first, second)
        self.reverse_path.append(path)

    def message(self):
        return super().message() + \
               [ 'Merge over immutable in: ',
                 self.first.url,
                 self.second.url ]


class FrozenHierarchy(ProcessError):
    def __init__(self, url, hierarchy_type):
        super().__init__()
        self.url = url
        self.hierarchy_type = hierarchy_type

    def message(self):
        return super().message() + \
               [ 'Internal error: attempt to change frozen hierarchy',
                 'url: {0}'.format(self.url) ] + \
               self.traceback()


class NotHierarchy(ProcessError):
    def __init__(self, url, hierarchy_type, other):
        super().__init__()
        self.url = url
        self.hierarchy_type = hierarchy_type
        self.other = other

    def message(self):
        return super().message() + \
               [ 'Internal error: attempt to merge non hierarchy object',
                 'url: {0}'.format(self.url),
                 'other type: {0}'.format(type(self.other)) ] + \
               self.traceback()


class NoSuchPath(Exception):
    def __init__(self, missing_path):
        super().__init__()
        self.missing_path = missing_path
