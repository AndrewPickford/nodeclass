#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from reclass.invquery.parser import Parser
from reclass.utils.path import Path
from .item import Item


class InvQuery(Item):
    ''' Holds an inventory query
    '''

    invquery_parser = Parser(Path)

    def __init__(self, inv_query):
        super().__init__(None)
        self.contents = self.invquery_parser.parse(inv_query.render())
        print(repr(self.contents))
        self.unresolved = True

    def inventory_query(self):
        return self.contents

    def resolve_to_item(self, context, inventory):
        pass
