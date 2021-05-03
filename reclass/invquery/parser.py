from .exceptions import InventoryQueryParseError
from .query import IfQuery as BaseIfQuery
from .query import ListIfQuery as BaseListIfQuery
from .query import QueryOptions
from .query import ValueQuery as BaseValueQuery
from .parser_functions import inventory_query_parser, Tags


class Parser:
    '''
    '''
    IfQuery = BaseIfQuery
    ListIfQuery = BaseListIfQuery
    ValueQuery = BaseValueQuery

    def __init__(self):
        self.expression_parser = inventory_query_parser()
        self._query_type = {
            Tags.IF_QUERY.value: self.IfQuery,
            Tags.LIST_IF_QUERY.value: self.ListIfQuery,
            Tags.VALUE_QUERY.value: self.ValueQuery
        }

    def parse(self, expression):
        tokens = self.expression_parser.parseString(expression.strip())
        try:
            options = QueryOptions()
            pos = 0
            while tokens[pos].type == Tags.OPTION.value:
                options.set(tokens[pos].data)
                pos += 1
            query = tokens[pos]
            if query.type in self._query_type:
                return self._query_type[query.type](query.data, options)
            raise InventoryQueryParseError(tokens, 'unknown query type')
        except InventoryQueryParseError as exc:
           exc.tokens = tokens
           raise
        except:
           raise InventoryQueryParseError(tokens, 'unknown error')
