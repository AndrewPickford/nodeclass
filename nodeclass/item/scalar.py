#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from .item import Renderable

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..interpolator.inventory import InventoryDict
    from ..value.hierarchy import Hierarchy
    from .item import RenderableValue


class Scalar(Renderable):
    ''' Holds either an int, float, bool or string
    '''

    def __init__(self, contents: 'RenderableValue'):
        super().__init__(contents)

    def resolve_to_item(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Scalar':
        ''' Already resolved, return self
        '''
        return self

    def render(self) -> 'RenderableValue':
        ''' Return the Item contents
        '''
        return self.contents
