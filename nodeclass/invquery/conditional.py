from ..value.value import ValueType
from .comparision import Comparision
from .exceptions import InventoryQueryParseError, InventoryQueryValueNotRenderable
from .operand import Operand

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Set
    from .tokenizer import Token
    from ..utils.path import Path
    from ..value.hierarchy import Hierarchy


class Conditional:
    def __init__(self, lhs_token: 'Token', comp_token: 'Token', rhs_token: 'Token'):
        self.lhs = Operand.FromToken(lhs_token)
        self.comparision = Comparision(comp_token)
        self.rhs = Operand.FromToken(rhs_token)
        if Operand.is_export(self.lhs) and Operand.is_export(self.rhs):
            raise InventoryQueryParseError('two exports defined in comparision: {0}'.format(str(self)))
        elif Operand.is_export(self.lhs):
            self.export = self.lhs
            self.other = self.rhs
        elif Operand.is_export(self.rhs):
            self.export = self.rhs
            self.other = self.lhs
        else:
            raise InventoryQueryParseError('no exports defined in comparision: {0}'.format(str(self)))

    def __eq_(self, other: 'Any') -> 'bool':
        if self.__class__ == other.__class__:
            if self.lhs == other.lhs and self.comparision == other.comparision and self.rhs == other.rhs:
                return True
        return False

    def __ne__(self, other: 'Any') -> 'bool':
        return not self.__eq__(other)

    def __str__(self) -> 'str':
        return '{0} {1} {2}'.format(self.lhs, self.comparision, self.rhs)

    def __repr__(self) -> 'str':
        return '{0}({1} {2} {3})'.format(self.__class__.__name__, repr(self.lhs), repr(self.comparision), repr(self.rhs))

    def evaluate(self, node_exports: 'Hierarchy', context: 'Hierarchy') -> 'bool':
        if self.export.path not in node_exports:
            return False
        value = node_exports[self.export.path]
        if not ValueType.is_renderable(value):
            raise InventoryQueryValueNotRenderable(self.export.path, value)
        export = value.render_all()
        if Operand.is_pathed(self.other):
            value = context[self.other.path]
            if not ValueType.is_renderable(value):
                raise InventoryQueryValueNotRenderable(self.other.path, value)
            other = value.render_all()
        else:
            other = self.other.data
        return self.comparision.compare(export, other)

    @property
    def exports(self) -> 'Set[Path]':
        return self.lhs.exports | self.rhs.exports

    @property
    def references(self) -> 'Set[Path]':
        return self.lhs.references | self.rhs.references
