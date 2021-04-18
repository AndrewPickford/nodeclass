#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from enum import Enum
from .exceptions import ItemRenderUndefinedError


class Item:
    '''
    Abstract base class defining the interface to Item objects.

    Item objects should be treated as immutable.

    A complex item contains unresolved references or inventory queries and
    cannot be rendered.
    '''

    def __init__(self, contents):
        self.contents = contents
        self.complex = False

    @property
    def references(self):
        '''
        List of paths referenced by this item
        '''
        return []

    @property
    def inventory_queries(self):
        '''
        List of inventory queries required
        '''
        return []

    def resolve(self, context, inventory):
        '''
        Look up in the context and inventory dictionaries any references or inventory
        queries and return the item found in the lookup.

        In the case of nested references, ${one_${two}}, resolve the inner most reference
        and return a new reference item.

        If an item has no references or inventory queries return self.

        context: Value.Dictionary
        inventory: Value.Dictionary
        returns: Item
        '''
        raise ItemResolveUndefinedError(self)

    def render(self):
        '''
        Returns the item as either an int, float, bool or string.

        Only defined for scalar or composite items.
        '''
        raise ItemRenderUndefinedError(self)

    def __str__(self):
        return str(self.contents)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, repr(self.contents))
