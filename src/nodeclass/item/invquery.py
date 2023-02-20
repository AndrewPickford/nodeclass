#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from .exceptions import InvQueryRender, InvQueryResolveToItem
from .item import Item

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Set
    from ..interpolator.inventory import InventoryDict
    from ..invquery.query import Query
    from ..utils.path import Path
    from ..value.hierarchy import Hierarchy
    from ..value.value import Value
    from .item import RenderableValue


class InvQuery(Item):
    ''' Holds an inventory query
    '''

    def __init__(self, inv_query: 'Query'):
        self.contents: Query
        super().__init__(inv_query)
        self.unresolved = True

    @property
    def inventory_query(self) -> 'Query':
        return self.contents

    @property
    def references(self) -> 'Set[Path]':
        return self.contents.references

    def description(self) -> 'str':
        return 'InvQuery({0})'.format(str(self.contents))

    def render(self) -> 'RenderableValue':
        raise InvQueryRender(self)

    def resolve_to_item(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Item':
        raise InvQueryResolveToItem(self)

    def resolve_to_value(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Value':
        return self.contents.evaluate(context, inventory, environment)
