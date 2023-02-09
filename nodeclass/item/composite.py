#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from .exceptions import ItemResolveError
from .item import Item
from .scalar import Scalar

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Set
    from ..interpolator.inventory import InventoryDict
    from ..utils.path import Path
    from ..value.hierarchy import Hierarchy
    from .item import RenderableValue


class Composite(Item):
    '''
    Holds a list of other Scalar or Reference Items. Inventory queries cannot be
    part of a composite item.

    A Composite item is rendered to a string, or in the unusal but valid case of a
    Composite item holding only a single Item the contained Item is rendered without
    forcing it into a string representation.
    '''

    __slots__ = ('_references')

    def __init__(self, items: 'List[Item]'):
        self.contents: 'List[Item]'
        self._references: 'Set[Path]'
        super().__init__(items)
        self._references = set()
        for i in self.contents:
            if i.unresolved:
                self.unresolved = True
                self._references |= i.references

    def __str__(self) -> 'str':
        return ''.join(map(str, self.contents))

    @property
    def references(self) -> 'Set[Path]':
        return self._references

    def description(self) -> 'str':
        return 'Composite({0})'.format(str(self))

    def resolve_to_item(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Item':
        '''
        '''
        if len(self._references) > 0:
            try:
                items = [ i.resolve_to_item(context, inventory, environment) for i in self.contents ]
                comp = type(self)(items)
                if len(comp._references) > 0:
                    # nested references, return Item for later resolving
                    return comp
                else:
                    # all references resolved, flatten Item
                    return comp.flatten()
            except ItemResolveError:
                raise ItemResolveError(self)
        else:
            # no unresolved references so flatten to a single Scalar Item
            return self.flatten()

    def resolve_to_value(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'None':
        '''
        Composite items cannot resolve directly to a Value, so return None to
        indicate to use resolve_to_item.
        '''
        return None

    def flatten(self) -> 'Item':
        '''
        Join the composites parts into a single Scalar Item
        '''
        if len(self.contents) == 1:
            return self.contents[0]
        else:
            return Scalar(''.join([ str(i.render()) for i in self.contents ]))

    def render(self) -> 'RenderableValue':
        '''
        Return the render of the flattened contents
        '''
        return self.flatten().render()
