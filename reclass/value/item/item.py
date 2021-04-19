#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from abc import ABC, abstractmethod

from enum import Enum
from .exceptions import ItemRenderUndefinedError


class Item(ABC):
    '''
    Abstract base class defining the interface to Item objects.

    Item objects should be treated as immutable.

    An item with self.unresolved == True contains has unresolved references and cannot
    be rendered.
    '''

    def __init__(self, contents):
        self.contents = contents
        self.unresolved = False

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, repr(self.contents))

    def __str__(self):
        return str(self.contents)

    def references(self):
        '''
        List of paths referenced by this Item
        '''
        return []

    def inventory_queries(self):
        '''
        List of inventory queries required
        '''
        return []

    @abstractmethod
    def resolve(self, context, inventory):
        '''
        For references look up in the context dictionary the referenced Item and return it.

        For nested references, such as ${one_${two}}, resolve the inner most reference
        and return a new reference item.

        For inventory queries using the context and inventory dictionaries return a new Item
        representing the queries answer.

        If an Item has no references or inventory queries return self.

        context: Value.Dictionary
        inventory: Value.Dictionary
        returns: Item
        '''
        pass
