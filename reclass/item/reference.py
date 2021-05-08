#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from ..utils.path import Path
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
            self._references = self.contents.references
        else:
            self._references = { Path.fromstring(self.contents.render()) }

    def __str__(self):
        rs = self.settings.reference_sentinels
        return '{0}{1}{2}'.format(rs[0], self.contents, rs[1])

    @property
    def references(self):
        return self._references

    def resolve_to_item(self, context, inventory, environment):
        '''
        Resolve one level of indirection, returning a new Item. This handles
        nested references.

        It is an error here for references to resolve to Dictionary, List or Merge
        Values as they should have already been handled by resolve_to_value.

        context: Dictionary of parameters
        inventory: Dictionary of inventory query answers
        environment: Environment to evaluate inventory queries in
        returns: resolved Item
        '''
        if self.contents.unresolved:
            ref = self.contents.resolve_to_item(context, inventory, environment)
            return Reference(ref)
        else:
            path = Path.fromstring(str(self.contents.render()))
            try:
                return context[path].item
            except ItemResolveError:
                raise ItemResolveError(self)

    def resolve_to_value(self, context, inventory, environment):
        '''
        Resolve one level of indirection, returning the Value this reference
        is pointing at. This handles simple single references, such as ${foo},
        regardless of what type of Value the reference is pointing at.

        In the case of nested references return None, indicating a call to
        resolve_to_item is required to get a new Item for wrapping in a Plain
        Value.

        context: Dictionary of parameters
        inventory: Dictionary of inventory query answers
        environment: Environment to evaluate inventory queries in
        returns: a new Value or None
        '''
        if self.contents.unresolved:
            return None
        path = Path.fromstring(str(self.contents.render()))
        try:
            return context[path]
        except KeyError:
            raise ItemResolveError(self)
