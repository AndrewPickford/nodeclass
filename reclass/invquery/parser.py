from .exceptions import InventoryQueryParseError
from .query import IfQuery, ListIfQuery, ValueQuery
from .parser_functions import inventory_query_parser, Tags


class Parser:
    '''
    '''

    _query_type = {
        Tags.IF_QUERY.value: IfQuery,
        Tags.LIST_IF_QUERY.value: ListIfQuery,
        Tags.VALUE_QUERY.value: ValueQuery
    }

    def __init__(self, path_class):
        self.Path = path_class
        self.expression_parser = inventory_query_parser()

    def parse(self, expression):
        tokens = self.expression_parser.parseString(expression.strip())
        try:
            query = tokens[0]
            if query.type in self._query_type:
                return self._query_type[query.type](query.data)
            raise InventoryQueryParseError(tokens, 'unknown query type')
        except InventoryQueryParseError as exc:
           exec.tokens = tokens
           raise
        except:
           raise InventoryQueryParseError(tokens, 'unknown error')
