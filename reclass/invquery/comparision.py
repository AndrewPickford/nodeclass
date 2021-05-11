import operator
from .exceptions import InventoryQueryParseError
from .tokenizer import Tags


class Comparision:
    def __init__(self, token):
        if token.type != Tags.COMPARISION.value:
            raise InventoryQueryParseError('expected comparision operator, found: {0}'.format(token))
        if token.data == '==':
            self.op = operator.eq
        elif token.data == '!=':
            self.op = operator.ne
        else:
            raise InventoryQueryParseError('error parsing comparision: {0}'.format(token))

    def __eq_(self, other):
        if self.__class__ == other.__class__:
            if self.op == other.op:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '==' if self.op == operator.eq else '!='

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    def compare(self, lhs, rhs):
        return self.op(lhs, rhs)
