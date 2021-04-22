#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
import pyparsing as pp

from reclass.settings import SETTINGS
from .composite import Composite
from .exceptions import ParseError
from .functions import full_parser, simple_parser, Tags
from .invquery import InvQuery
from .reference import Reference
from .scalar import Scalar

class Parser:
    '''
    A wrapper class to hide the complexity of parsing a string.

    Usage: create a Parser object then use the parse method on a
    string to create the Item representation of that string:

    parser = Parser()
    item = parser.parse('bar is ${foo}')
    '''

    def __init__(self):
        self.full_parser = full_parser()
        self.simple_parser = simple_parser()
        self.ref_sent = SETTINGS.reference_sentinels[0]
        self.inv_query_sent = SETTINGS.inv_query_sentinels[0]

    def parse(self, input):
        '''
        Translate a string input into it's Item representation. Returns a single
        item.

        input: string to parse
        returns: the Item representation of the string
        '''
        def use_full_parser(input):
            try:
                return self.full_parser.parseString(input)
            except pp.ParseException as e:
                raise ParseError(input, e.col)

        sentinel_count = input.count(self.ref_sent) + input.count(self.inv_query_sent)
        if sentinel_count == 0:
            # speed up: if there are no sentinels in the string then do not parse
            # the input string as the returned item must be a simple scalar item
            # containg the string
            return Scalar(input)
        elif sentinel_count == 1:
            # speed up: if only a single sentinel is present then it is most likely
            # a simple reference so try the simpler and much faster single reference
            # parser first
            try:
                tokens = self.simple_parser.parseString(input)
            except pp.ParseException:
                # the single reference parser failed so try the full parser
                tokens = use_full_parser(input)
        else:
            # use the full parser when more than one sentinel is present
            tokens = use_full_parser(input)

        items = self._create_items(tokens)
        if len(items) == 1:
            return items[0]
        return Composite(items)

    _item_builders = { Tags.STR.value: (lambda s, v: Scalar(v)),
                       Tags.REF.value: (lambda s, v: s._create_ref(v)),
                       Tags.INV.value: (lambda s, v: s._create_inv(v)) }

    @classmethod
    def _create_items(cls, tokens):
        return [ cls._item_builders[t](cls, v) for t, v in tokens ]

    @classmethod
    def _create_ref(cls, tokens):
        items = [ cls._item_builders[t](cls, v) for t, v in tokens ]
        if len(items) == 1:
            return Reference(items[0])
        else:
            return Reference(Composite(items))

    @classmethod
    def _create_inv(cls, tokens):
        items = [ Scalar(v) for t, v in tokens ]
        if len(items) == 1:
            return InvQuery(items[0])
        return InvQuery(Composite(items))

