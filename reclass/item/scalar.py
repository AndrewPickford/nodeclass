#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from .item import Item


class Scalar(Item):
    ''' Holds either an int, float, bool or string
    '''

    def __init__(self, contents):
        super().__init__(contents)

    def resolve_to_item(self, context, inventory):
        ''' Already resolved, return self
        '''
        return self

    def render(self):
        ''' Return the Item contents
        '''
        return self.contents
