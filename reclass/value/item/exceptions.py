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
