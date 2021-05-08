#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
import pyparsing as pp

from ..invquery.parser import Parser as InvQueryParser
from .composite import Composite
from .exceptions import ParseError
from .invquery import InvQuery
from .parser_functions import full_parser, simple_parser, Tags
from .reference import Reference
from .scalar import Scalar


class Parser:
    '''
    A wrapper class to hide the complexity of parsing a string.
    Thread local to allow different threads to use different settings.

    Usage: create a Parser object then use the parse method on a
    string to create the Item representation of that string:

    >>> parser = Parser()
    >>> item = parser.parse('bar is ${foo}')
    >>> print(str(item))
    bar is ${foo}
    >>> print(repr(item))
    Composite([Scalar('bar is '), Reference(Scalar('foo'))])
    '''

    def __init__(self, settings):
        self.full_parser = full_parser(settings)
        self.simple_parser = simple_parser(settings)
        self.invquery_parser = InvQueryParser()
        self.ref_sent = settings.reference_sentinels[0]
        self.invquery_sent = settings.inventory_query_sentinels[0]
        self.cache = {}

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

        if input in self.cache:
            return self.cache[input]

        sentinel_count = input.count(self.ref_sent) + input.count(self.invquery_sent)
        if sentinel_count == 0:
            # speed up: if there are no sentinels in the string then do not parse
            # the input string as the returned item must be a simple scalar item
            # containing the string
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
            item = items[0]
        else:
            item = Composite(items)
        self.cache[input] = item
        return item

    _item_builders = { Tags.STR.value: (lambda s, v: Scalar(v)),
                       Tags.REF.value: (lambda s, v: s._create_ref(v)),
                       Tags.INV.value: (lambda s, v: s._create_inv(v)) }

    def _create_items(self, tokens):
        return [ self._item_builders[t](self, v) for t, v in tokens ]

    def _create_ref(self, tokens):
        items = [ self._item_builders[t](self, v) for t, v in tokens ]
        if len(items) == 1:
            return Reference(items[0])
        else:
            return Reference(Composite(items))

    def _create_inv(self, tokens):
        expression = ''.join([ v for t, v in tokens ])
        query = self.invquery_parser.parse(expression)
        return InvQuery(query)
