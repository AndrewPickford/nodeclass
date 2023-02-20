#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from .exceptions import ScalarResolveToValue
from .item import Item

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..interpolator.inventory import InventoryDict
    from ..value.hierarchy import Hierarchy
    from .item import RenderableValue

class Scalar(Item):
    ''' Holds either an int, float, bool or string
    '''

    def __init__(self, contents: 'RenderableValue'):
        super().__init__(contents)

    def description(self) -> 'str':
        return 'Scalar({0})'.format(repr(self.contents))

    def resolve_to_item(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Scalar':
        ''' Already resolved, return self. Composite items will call here in their resolve_to_item method
            if one one of their composite items is a Scalar item.
        '''
        return self

    def resolve_to_value(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'None':
        ''' The interpolator should never call resolve_to_value on a Scalar item. So raise an error.
        '''
        raise ScalarResolveToValue(self)

    def render(self) -> 'RenderableValue':
        ''' Return the Item contents
        '''
        return self.contents
