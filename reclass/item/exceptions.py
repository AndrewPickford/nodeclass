#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#


class ItemError(Exception):
    def __init__(self, item):
        super().__init__()
        self.item = item
        self.message = []

    def __str__(self):
        message = '\n'.join(self.message)
        return message


class ItemRenderUndefinedError(ItemError):
    def __init__(self, item):
        super().__init__(item)


class ItemResolveError(ItemError):
    def __init__(self, item):
        super().__init__(item)
        self.message.append('Unable to resolve item {0}'.format(item))


class ParseError(Exception):
    def __init__(self, input, location):
        super().__init__()
        self.input = input
        self.location = location

    def __str__(self):
        return 'Parse error at position {0} with input: {1}'.format(self.location, self.input)
