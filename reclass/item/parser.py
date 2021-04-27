#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
import pyparsing as pp

from reclass.utils.path import Path
from .composite import Composite
from .exceptions import ParseError
from .functions import full_parser, simple_parser, Tags
from .invquery import InvQuery
from .reference import Reference
from .scalar import Scalar


class Parser():
    '''
    A wrapper class to hide the complexity of parsing a string.
    Thread local to allow different threads to use different settings.

    Usage: create a Parser object then use the parse method on a
    string to create the Item representation of that string:

    parser = Parser()
    item = parser.parse('bar is ${foo}')
    '''

    def __init__(self, settings):
        self.full_parser = full_parser(settings)
        self.simple_parser = simple_parser(settings)
        self.ref_sent = settings.reference_sentinels[0]
        self.inv_query_sent = settings.inv_query_sentinels[0]
        self.path_split = settings.path_split
        self.Path = type('CustomPath', (Path, ), { 'delimiter': settings.delimiter })
        self.Scalar = Scalar
        self.Reference = type('CustomReference', (Reference, ), { 'path': self.Path, 'settings': settings })
        self.Composite = type('CustomComposite', (Composite, ), { 'scalar': self.Scalar, 'settings': settings })
        self.InvQuery = type('CustomInvQuery', (InvQuery, ), { 'settings': settings })

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
        return self.Composite(items)

    _item_builders = { Tags.STR.value: (lambda s, v: Scalar(v)),
                       Tags.REF.value: (lambda s, v: s._create_ref(v)),
                       Tags.INV.value: (lambda s, v: s._create_inv(v)) }

    def _create_items(self, tokens):
        return [ self._item_builders[t](self, v) for t, v in tokens ]

    def _create_ref(self, tokens):
        items = [ self._item_builders[t](self, v) for t, v in tokens ]
        if len(items) == 1:
            return self.Reference(items[0])
        else:
            return self.Reference(self.Composite(items))

    def _create_inv(self, tokens):
        items = [ self.Scalar(v) for t, v in tokens ]
        if len(items) == 1:
            return self.InvQuery(items[0])
        return self.InvQuery(self.Composite(items))
