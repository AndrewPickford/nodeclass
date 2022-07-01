from __future__ import annotations
from typing import TYPE_CHECKING

from .comparision import Comparision
from .exceptions import InventoryQueryParseError
from .operand import Operand
from .tokenizer import Tag

if TYPE_CHECKING:
    from typing import Any
    from ..value.hierarchy import Hierarchy
    from .tokenizer import Token


class Conditional:
    def __init__(self, lhs_token: Token, comp_token: Token, rhs_token: Token):
        self.lhs = Operand(lhs_token)
        self.comparision = Comparision(comp_token)
        self.rhs = Operand(rhs_token)
        if Tag.EXPORT.value not in [ self.lhs.type, self.rhs.type ]:
            raise InventoryQueryParseError('no exports defined in comparision: {0}'.format(str(self)))
        elif self.lhs.type == Tag.EXPORT.value and self.rhs.type == Tag.EXPORT.value:
            raise InventoryQueryParseError('two exports defined in comparision: {0}'.format(str(self)))
        if self.lhs.type == Tag.EXPORT.value:
            self.export = self.lhs
            self.other = self.rhs
        else:
            self.export = self.rhs
            self.other = self.lhs

    def __eq_(self, other: Any) -> bool:
        if self.__class__ == other.__class__:
            if self.lhs == other.lhs and self.comparision == other.comparision and self.rhs == other.rhs:
                return True
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return '{0} {1} {2}'.format(self.lhs, self.comparision, self.rhs)

    def __repr__(self) -> str:
        return '{0}({1} {2} {3})'.format(self.__class__.__name__, repr(self.lhs), repr(self.comparision), repr(self.rhs))

    def evaluate(self, node_exports: Hierarchy, context: Hierarchy) -> bool:
        if self.export.path not in node_exports:
            return False
        export = node_exports[self.export.path].render_all()
        if self.other.type == Tag.PARAMETER.value:
            other = context[self.other.path].render_all()
        else:
            other = self.other.data
        return self.comparision.compare(export, other)

    @property
    def exports(self):
        return self.lhs.exports | self.rhs.exports

    @property
    def references(self):
        return self.lhs.references | self.rhs.references
