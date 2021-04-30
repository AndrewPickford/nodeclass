from .exceptions import InventoryQueryParseError
from .iftest import IfTest
from .operand import Operand
from .parser_functions import Tags

class Query:
    def __init__(self):
        self._hash = hash(str(self))

    def __hash__(self):
        return self._hash


class IfQuery(Query):
    def __init__(self, tokens):
        if tokens[0].type != Tags.EXPORT.value:
            raise InventoryQueryParseError(tokens, 'if queries begin with an export to return')
        if tokens[1].type != Tags.IF.value:
            raise InventoryQueryParseError(tokens, 'if queries begin with start with an export followed by "if"')
        self.returned = Operand(tokens[0])
        self.test = IfTest(tokens[2], tokens[3], tokens[4])
        super().__init__()

    def __eq_(self, other):
        if (self.returned, self.test) == (other.returned, other.test):
           return True
        else:
           return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '{0} if {1}'.format(self.returned, self.test)

    def __repr__(self):
        return '{0}({1} {2})'.format(self.__class__.__name__, repr(self.returned), repr(self.test))

    @property
    def exports(self):
        return self.returned.exports | self.test.exports

    @property
    def references(self):
        return self.returned.references | self.test.references


class ListIfQuery(Query):
    def __init__(self, tokens):
        if tokens[0].type != Tags.IF.value:
            raise InventoryQueryParseError(tokens, 'list if queries begin with "if"')
        self.test = IfTest(tokens[1], tokens[2], tokens[3])
        super().__init__()

    def __eq_(self, other):
        if self.test == other.test:
           return True
        else:
           return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return 'if {0}'.format(self.test)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, repr(self.test))

    @property
    def exports(self):
        return self.test.exports

    @property
    def references(self):
        return self.test.references


class ValueQuery(Query):
    def __init__(self, tokens):
        super().__init__()
