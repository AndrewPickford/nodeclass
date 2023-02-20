#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
import pyparsing
from ..context import CONTEXT
from ..invquery.parser import parse as parse_inventory_expression
from .composite import Composite
from .exceptions import BadParseToken, ParseError
from .invquery import InvQuery
from .reference import Reference
from .scalar import Scalar
from .tokenizer import Tag


def parse(input):
    '''
    Translate a string input into it's Item representation. Returns a single
    item.

    input: string to parse
    returns: the Item representation of the string
    '''

    def process_reference(tokens):
        items = [ process_token(tag, value) for tag, value in tokens ]
        if len(items) == 1:
            return Reference(items[0])
        else:
            return Reference(Composite(items))

    def process_inventory_query(tokens):
        expression = ''.join([ value for tag, value in tokens ])
        query = parse_inventory_expression(expression)
        return InvQuery(query)

    def process_token(tag, value):
        if tag == Tag.STR.value:
            return Scalar(value)
        elif tag == Tag.REF.value:
            return process_reference(value)
        elif tag == Tag.INV.value:
            return process_inventory_query(value)
        else:
            raise BadParseToken(tag, value)

    def use_full_parser(input):
        try:
            return CONTEXT.full_tokenizer.parseString(input)
        except pyparsing.ParseException as e:
            raise ParseError(input, e.col)

    if input in CONTEXT.item_parse_cache:
        return CONTEXT.item_parse_cache[input]

    sentinel_count = input.count(CONTEXT.settings.reference_sentinels[0]) + \
                     input.count(CONTEXT.settings.inventory_query_sentinels[0])

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
            tokens = CONTEXT.simple_tokenizer.parseString(input)
        except pyparsing.ParseException:
            # the single reference parser failed so try the full parser
            tokens = use_full_parser(input)
    else:
        # use the full parser when more than one sentinel is present
        tokens = use_full_parser(input)

    items = [ process_token(tag, value) for tag, value in tokens ]
    if len(items) == 1:
        item = items[0]
    else:
        item = Composite(items)
    CONTEXT.item_parse_cache[input] = item
    return item
