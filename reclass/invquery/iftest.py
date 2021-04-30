from .exceptions import InventoryQueryParseError
from .parser_functions import Tags
from .operand import Operand
from .operator import OpTest

class IfTest:
    def __init__(self, lhs_tokens, op_tokens, rhs_tokens):
        self.lhs = Operand(lhs_tokens)
        self.op = OpTest(op_tokens)
        self.rhs = Operand(rhs_tokens)
        if Tags.EXPORT.value not in [ self.lhs.type, self.rhs.type ]:
            raise InventoryQueryParseError(token, 'no exports defined in query')

    def __eq_(self, other):
        if self.lhs == other.lhs and self.op == other.op and self.rhs == other.rhs:
           return True
        else:
           return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '{0} {1} {2}'.format(self.lhs, self.op, self.rhs)

    def __repr__(self):
        return '{0}({1} {2} {3})'.format(self.__class__.__name__, repr(self.lhs), repr(self.op), repr(self.rhs))

    @property
    def exports(self):
        return self.lhs.exports | self.rhs.exports

    @property
    def references(self):
        return self.lhs.references | self.rhs.references
