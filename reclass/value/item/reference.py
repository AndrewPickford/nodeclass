#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from reclass.settings import SETTINGS
from reclass.utils.path import Path
from .exceptions import ItemResolveError
from .item import Item


class Reference(Item):
    '''
    A reference to another entry in the context dictionary.

    The contents of a Reference item is either a Scalar or a Composite item
    representing the path to the referenced entry.
    '''

    def __init__(self, item):
        super().__init__(item)
        self.unresolved = True
        if self.contents.unresolved:
            self._references = self.contents.references()
        else:
            self._references = [ Path.FromString(self.contents.render()) ]

    def __str__(self):
        rs = SETTINGS.reference_sentinels
        return '{0}{1}{2}'.format(rs[0], self.contents, rs[1])

    def references(self):
        return self._references

    def resolve(self, context, inventory):
        '''
        context: dictionary of already resolved Items, which are all renderable
            Items (Scalar or Composite)
        inventory: dictionary of inventory query answers, which are all
            renderable Items (Scalar or Composite)
        '''
        if self.contents.unresolved:
            try:
                return self.contents.resolve(context, inventory)
            except ItemResolveError as e:
                raise ItemResolveError(self)
        else:
            path = Path.FromString(self.contents.render())
            try:
                return context[path]
            except KeyError as e:
                raise ItemResolveError(self)
