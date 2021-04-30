from .exceptions import InventoryQueryParseError
from .parser_functions import Tags


class OpTest:
    def __init__(self, token):
        if token.type != Tags.OP_TEST.value:
            raise InventoryQueryParseError(token, 'unknown operator {0}'.format(token.data))
        if token.data == '==':
            self.negate = False
        elif token.data == '!=':
            self.negate = True
        else:
            raise InventoryQueryParseError(token, 'unknown operator {0}'.format(token.data))

    def __eq_(self, other):
        if self.negate == other.negate:
           return True
        else:
           return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '!=' if self.negate else '=='

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, str(self))
