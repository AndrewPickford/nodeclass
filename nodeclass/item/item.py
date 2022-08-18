#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Set, Union
    from ..interpolator.inventory import InventoryDict
    from ..invquery.query import Query
    from ..utils.path import Path
    from ..value.hierarchy import Hierarchy
    RenderableValue = Union[bool, float, int, str, None]


class Item(ABC):
    '''
    Abstract base class defining the interface to Item objects.

    Item objects should be treated as immutable.

    An item with self.unresolved == True contains has unresolved references and cannot
    be rendered.
    '''

    __slots__ = ('contents', 'unresolved')

    def __init__(self, contents: 'Any'):
        self.contents = contents
        self.unresolved = False

    def __eq__(self, other: 'Any') -> 'bool':
        if self.__class__ != other.__class__:
            return False
        if self.contents == other.contents:
            return True
        return False

    def __repr__(self) -> 'str':
        return '{0}({1})'.format(self.__class__.__name__, repr(self.contents))

    def __str__(self) -> 'str':
        return str(self.contents)

    @property
    def references(self) -> 'Set[Path]':
        '''
        Set of paths referenced by this Item
        '''
        return set()

    @property
    def inventory_query(self) -> 'Union[Query, None]':
        '''
        Return the inventory Query, if any of this Item or None if it does not have
        an inventory Query.
        '''
        return None

    @abstractmethod
    def resolve_to_item(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Item':
        '''
        Handle references which require a new Item when resolved.

        For nested references, such as ${one_${two}}, resolve the inner most reference
        and return a new reference Item.

        For inventory queries using the context and inventory dictionaries return a new Item
        representing the queries answer.

        If an Item has no references or inventory queries return self.

        context: Value.Dictionary
        inventory: Value.Dictionary
        environment: node environment
        returns: Item
        '''
        pass


class Renderable(Item):
    @abstractmethod
    def render(self) -> 'RenderableValue':
        pass

    @abstractmethod
    def resolve_to_item(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Renderable':
        pass
