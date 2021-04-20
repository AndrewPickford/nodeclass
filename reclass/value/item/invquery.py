#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from .item import Item


class InvQuery(Item):
    '''
    Dummy inventory query class
    '''

    def __init__(self, contents):
        super().__init__(contents)
