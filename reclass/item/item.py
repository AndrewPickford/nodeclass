#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from abc import ABC, abstractmethod
from reclass.settings import defaults


class Item(ABC):
    '''
    Abstract base class defining the interface to Item objects.

    Item objects should be treated as immutable.

    An item with self.unresolved == True contains has unresolved references and cannot
    be rendered.
    '''

    settings = defaults

    def __init__(self, contents):
        self.contents = contents
        self.unresolved = False

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, repr(self.contents))

    def __str__(self):
        return str(self.contents)

    @property
    def references(self):
        '''
        List of paths referenced by this Item
        '''
        return []

    def inventory_query(self):
        '''
        Inventory queries required
        '''
        return None

    @abstractmethod
    def resolve_to_item(self, context, inventory, settings):
        '''
        Handle references which require a new Item when resolved.

        For nested references, such as ${one_${two}}, resolve the inner most reference
        and return a new reference Item.

        For inventory queries using the context and inventory dictionaries return a new Item
        representing the queries answer.

        If an Item has no references or inventory queries return self.

        context: Value.Dictionary
        inventory: Value.Dictionary
        settings: control settings
        returns: Item
        '''
        pass
