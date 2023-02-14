from ..utils.path import Path
from .exceptions import InventoryQueryParseError
from .tokenizer import Tag

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    try:
        # Python 3.10 and above
        from typing import TypeGuard
    except ImportError:
        from typing_extensions import TypeGuard
    from typing import Any, Set
    from .tokenizer import Token




class Operand:
    @staticmethod
    def FromToken(token: 'Token') -> 'Operand':
        if token.type in [ Tag.EXPORT.value, Tag.PARAMETER.value ]:
            return OperandPathed(token)
        return Operand(token)

    @staticmethod
    def is_export(operand: 'Operand') -> 'TypeGuard[OperandPathed]':
        return operand.type == Tag.EXPORT.value

    @staticmethod
    def is_pathed(operand: 'Operand') -> 'TypeGuard[OperandPathed]':
        return operand.type in [ Tag.EXPORT.value, Tag.PARAMETER.value ]

    def __init__(self, token: 'Token'):
        if token.type not in [ Tag.STRING.value, Tag.BOOL.value, Tag.INT.value, Tag.FLOAT.value, Tag.EXPORT.value, Tag.PARAMETER.value ]:
            raise InventoryQueryParseError('expected operand found: {0}'.format(token))
        self.type = token.type
        self.data = token.data

    def __eq_(self, other: 'Any') -> 'bool':
        if self.__class__ == other.__class__:
            if self.type == other.type and self.data == other.data:
                return True
        return False

    def __ne__(self, other: 'Any') -> 'bool':
        return not self.__eq__(other)

    def __str__(self) -> 'str':
        if self.type == Tag.EXPORT.value:
            return 'exports:{0}'.format(self.data)
        elif self.type == Tag.PARAMETER.value:
            return 'parameters:{0}'.format(self.data)
        else:
            return str(self.data)

    def __repr__(self) -> 'str':
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    @property
    def exports(self) -> 'Set[Path]':
        if self.type == Tag.EXPORT.value:
            return { Path.fromstring(self.data) }
        return set()

    @property
    def references(self) -> 'Set[Path]':
        if self.type == Tag.PARAMETER.value:
            return { Path.fromstring(self.data) }
        return set()


class OperandPathed(Operand):
    def __init__(self, token: 'Token'):
        super().__init__(token)
        if token.type not in [ Tag.EXPORT.value, Tag.PARAMETER.value ]:
            raise InventoryQueryParseError('expected export or parameter found: {0}'.format(token))
        self.path = Path.fromstring(self.data)
