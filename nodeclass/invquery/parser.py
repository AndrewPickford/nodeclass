from __future__ import annotations
from typing import TYPE_CHECKING

import pyparsing
from ..context import CONTEXT
from .exceptions import InventoryQueryParseError
from .query import IfQuery
from .query import ListIfQuery
from .query import QueryOptions
from .query import ValueQuery
from .tokenizer import Tags

if TYPE_CHECKING:
    from .query import Query

QUERY_TYPE_LOOKUP = {
    Tags.IF_QUERY.value: IfQuery,
    Tags.LIST_IF_QUERY.value: ListIfQuery,
    Tags.VALUE_QUERY.value: ValueQuery
}

def parse(expression: str) -> Query:
    try:
        tokens = CONTEXT.expression_tokenizer.parseString(expression.strip())
    except pyparsing.ParseException:
        raise InventoryQueryParseError('tokenizer error', expression)
    try:
        options = QueryOptions()
        pos = 0
        while tokens[pos].type == Tags.OPTION.value:
            options.set(tokens[pos].data)
            pos += 1
        query = tokens[pos]
        if query.type in QUERY_TYPE_LOOKUP:
            return QUERY_TYPE_LOOKUP[query.type](query.data, options)
        raise InventoryQueryParseError('unknown query type', expression)
    except InventoryQueryParseError as exception:
        exception.expression = expression
        raise
    except Exception as exception:
        raise InventoryQueryParseError(str(exception), expression)
