#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from .exceptions import InvQueryResolveToItem
from .item import Item

class InvQuery(Item):
    ''' Holds an inventory query
    '''

    def __init__(self, inv_query):
        super().__init__(inv_query)
        self.unresolved = True

    @property
    def inventory_query(self):
        return self.contents

    @property
    def references(self):
        return self.contents.references

    def resolve_to_item(self, context, inventory, environment):
        raise InvQueryResolveToItem(self)

    def resolve_to_value(self, context, inventory, environment):
        return self.contents.evaluate(context, inventory, environment)
