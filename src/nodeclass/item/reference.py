#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from ..context import CONTEXT
from ..utils.path import Path
from ..value.value import ValueType
from .exceptions import ItemResolveError, ReferenceRender
from .item import Item

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Set, Union
    from ..interpolator.inventory import InventoryDict
    from ..value.hierarchy import Hierarchy
    from ..value.value import Value
    from .item import RenderableValue


class Reference(Item):
    '''
    A reference to another entry in the context dictionary.

    The contents of a Reference item is either a Scalar or a Composite item
    representing the path to the referenced entry.
    '''

    __slots__ = ('_references')

    def __init__(self, item: 'Item'):
        self.contents: 'Item'
        super().__init__(item)
        self.unresolved = True
        if self.contents.unresolved:
            self._references = self.contents.references
        else:
            self._references = { Path.fromstring(str(self.contents.render())) }

    def __str__(self) -> 'str':
        rs = CONTEXT.settings.reference_sentinels
        return '{0}{1}{2}'.format(rs[0], self.contents, rs[1])

    @property
    def references(self) -> 'Set[Path]':
        return self._references

    def description(self) -> 'str':
        return 'Ref({0})'.format(str(self))

    def render(self) -> 'RenderableValue':
        raise ReferenceRender(self)

    def resolve_to_item(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Item':
        '''
        Resolve one level of indirection, returning a new Item. This handles
        nested references.

        It is an error here for references to resolve to Dictionary, List or Merge
        Values as they should have already been handled by resolve_to_value.

        Returns the resolved Item.
        '''
        if self.contents.unresolved:
            ref = self.contents.resolve_to_item(context, inventory, environment)
            return Reference(ref)
        else:
            path = Path.fromstring(str(self.contents.render()))
            value = context[path]
            if ValueType.is_plain(value):
                # The Value at context[path] should be a Plain Value as Dictionary, List or Merge
                # Values should have already been handled by resolve_to_value.
                return value.item
            raise ItemResolveError(self)

    def resolve_to_value(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Union[Value, None]':
        '''
        Resolve one level of indirection, returning the Value this reference
        is pointing at. This handles simple single references, such as ${foo},
        regardless of what type of Value the reference is pointing at.

        In the case of nested references return None, indicating a call to
        resolve_to_item is required to get a new Item for wrapping in a Plain
        Value.
        '''
        if self.contents.unresolved:
            return None
        path = Path.fromstring(str(self.contents.render()))
        try:
            return context[path]
        except KeyError:
            raise ItemResolveError(self)
