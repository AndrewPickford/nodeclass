#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from .exceptions import ItemResolveError
from .item import Item


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
        for i in self.contents:
            if i.unresolved:
                self._references.extend(i.references())
        if len(self._references) > 0:
            self.unresolved = True

    def __str__(self):
        return ''.join(map(str, self.contents))

    def references(self):
        return self._references

    def resolve(self, context, inventory):
        if self.unresolved:
            try:
                items = [ i.resolve(context,inventory) for i in self.contents ]
                return Composite(items)
            except ItemResolveError as e:
                raise ItemResolveError(self)
        else:
            return self

    def render(self):
        # Preserve type if only one item
        if len(self.contents) == 1:
            return self.contents[0].render()
        # Multiple items, concatenate into a string
        return ''.join([ str(i.render()) for i in self.contents ])
