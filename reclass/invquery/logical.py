import operator
from .exceptions import InventoryQueryParseError
from .tokenizer import Tags


class Logical:
    def __init__(self, token):
        if token.type != Tags.LOGICAL.value:
            raise InventoryQueryParseError(token, 'expected a logical operator, found: {0}'.format(token))
        data = token.data.lower()
        if data == 'or':
            self.op = operator.or_
        elif data == 'and':
            self.op = operator.and_
        else:
            raise InventoryQueryParseError(token, 'error parsing logical: {0}'.format(token))

    def __eq_(self, other):
        if self.__class__ == other.__class__:
            if self.op == other.op:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return 'or' if self.op == operator.or_ else 'and'

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    def combine(self, lhs, rhs):
        return self.op(lhs, rhs)
