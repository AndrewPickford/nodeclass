#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from .item import Item

class InvQuery(Item):
    ''' Holds an inventory query
    '''

    def __init__(self, inv_query):
        super().__init__(None)
        self.contents = inv_query
        self.unresolved = True

    @property
    def inventory_query(self):
        return self.contents

    @property
    def references(self):
        return self.contents.references

    def resolve_to_item(self, context, inventory, environment):
        raise RuntimeError('InvQuery reached resolve to item, which should never happen. [{0}]'.format(repr(self)))

    def resolve_to_value(self, context, inventory, environment):
        return self.contents.evaluate(context, inventory, environment)
