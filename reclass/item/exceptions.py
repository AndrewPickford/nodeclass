#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from ..exceptions import InputError, InterpolationError


class ItemError(InterpolationError):
    def __init__(self, item):
        super().__init__()
        self.item = item

    def message(self):
        return super().message() + \
               [ 'Item: {0}'.format(self.item) ]


class InvQueryResolveToItem(ItemError):
    def __init__(self, item):
        super().__init__(item)

    def message(self):
        return super().message() + \
               [ 'Internal error: InvQuery reached resolve to item' ] + \
               self.traceback()


class ItemRenderUndefinedError(ItemError):
    def __init__(self, item):
        super().__init__(item)

    def message(self):
        return super().message() + \
               [ 'Item render undefined error' ]


class ItemResolveError(ItemError):
    def __init__(self, item):
        super().__init__(item)

    def message(self):
        return super().message() + \
               [ 'Item resolve error' ]


class ParseError(InputError):
    def __init__(self, input, location):
        super().__init__()
        self.input = input
        self.location = location

    def message(self):
        return super().message() + \
               [ 'Parse error',
                 'Position: {0}'.format(self.location),
                 'Input: {0}'.format(self.input) ]


class BadParseToken(InputError):
    def __init__(self, tag, value):
        super().__init__()
        self.tag = tag
        self.value = value

    def message(self):
        return super().message() + \
               [ 'Bad parse token',
                 'Tag: {0}'.format(self.tag),
                 'Value: {0}'.format(self.value) ] + \
               self.traceback()
