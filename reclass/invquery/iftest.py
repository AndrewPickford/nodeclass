from .exceptions import InventoryQueryParseError
from .parser_functions import Tags
from .operand import Operand
from .operator import OpTest

class IfTest:
    def __init__(self, lhs_token, op_token, rhs_token):
        self.lhs = Operand(lhs_token)
        self.op = OpTest(op_token)
        self.rhs = Operand(rhs_token)
        if Tags.EXPORT.value not in [ self.lhs.type, self.rhs.type ]:
            raise InventoryQueryParseError([self.lhs.type, self.rhs.typ], 'no exports defined in query')
        if self.lhs.type == Tags.EXPORT.value:
            self.export = self.lhs
            self.other = self.rhs
        else:
            self.export = self.rhs
            self.other = self.lhs

    def __eq_(self, other):
        if self.__class__ == other.__class__:
            if self.lhs == other.lhs and self.op == other.op and self.rhs == other.rhs:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '{0} {1} {2}'.format(self.lhs, self.op, self.rhs)

    def __repr__(self):
        return '{0}({1} {2} {3})'.format(self.__class__.__name__, repr(self.lhs), repr(self.op), repr(self.rhs))

    def evaluate(self, node_exports, context):
        if self.export.path not in node_exports:
            return False
        export = node_exports[self.export.path].render()
        if self.other.type == Tags.PARAMETER.value:
            other = context[self.other.path].render()
        else:
            other = self.other.data
        return export == other

    @property
    def exports(self):
        return self.lhs.exports | self.rhs.exports

    @property
    def references(self):
        return self.lhs.references | self.rhs.references
