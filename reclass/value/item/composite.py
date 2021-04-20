#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from .exceptions import ItemResolveError
from .item import Item
from .scalar import Scalar


class Composite(Item):
    '''
    Holds a list of other Scalar or Reference Items. Inventory queries cannot be
    part of a composite item.

    A Composite item is rendered to a string, or in the unusal but valid case of a
    Composite item holding only a single item the contained item is rendered without
    forcing it into a string representation.
    '''

    def __init__(self, items):
        super().__init__(items)
        self._references = []
        self.unresolved = True
        for i in self.contents:
            if i.unresolved:
                self._references.extend(i.references())

    def __str__(self):
        return ''.join(map(str, self.contents))

    def references(self):
        return self._references

    def resolve_to_item(self, context, inventory):
        if len(self._references) > 0:
            try:
                items = [ i.resolve_to_item(context,inventory) for i in self.contents ]
                return Composite(items)
            except ItemResolveError as e:
                raise ItemResolveError(self)
        else:
            # no unresolved references so flatten to a single Scalar Item
            if len(self.contents) == 1:
                return self.contents[0]
            else:
                return Scalar(''.join([ str(i.render()) for i in self.contents ]))

    def resolve_to_value(self, context, inventory):
        '''
        Composite items cannot resolve directly to a Value
        '''
        return None
