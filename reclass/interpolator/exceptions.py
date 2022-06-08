#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from ..exceptions import ProcessError


class NoSuchReference(ProcessError):
    def __init__(self, url, path, reference):
        super().__init__()
        self.url = url
        self.path = path
        self.reference = reference

    def message(self):
        return super().message() + \
               [ 'No such reference: {0}'.format(self.reference) ]


class ExcessivePathRevisits(ProcessError):
    def __init__(self, url, path):
        super().__init__()
        self.url = url
        self.path = path

    def message(self):
        return super().message() + \
               [ 'Internal error: Too many path revisits during interpolation' ] + \
               self.traceback()


class CircularReference(ProcessError):
    def __init__(self, url, path, reference):
        super().__init__()
        self.url = url
        self.path = path
        self.reference = reference

    def message(self):
        return super().message() + \
               [ 'Circular reference: {0}'.format(self.reference) ]
