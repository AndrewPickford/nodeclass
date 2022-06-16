#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from .item import Item


class Scalar(Item):
    ''' Holds either an int, float, bool or string
    '''

    def __init__(self, contents):
        super().__init__(contents)

    def resolve_to_item(self, context, inventory, environment):
        ''' Already resolved, return self
        '''
        return self

    def render(self):
        ''' Return the Item contents
        '''
        return self.contents
