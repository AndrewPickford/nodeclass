from __future__ import annotations
from typing import TYPE_CHECKING

from ..utils.path import Path
from .exceptions import InventoryQueryParseError
from .tokenizer import Tags

if TYPE_CHECKING:
    from typing import Any
    from .tokenizer import Token


class Operand:
    def __init__(self, token: Token):
        if token.type not in [ Tags.STRING.value, Tags.BOOL.value, Tags.INT.value, Tags.FLOAT.value, Tags.EXPORT.value, Tags.PARAMETER.value ]:
            raise InventoryQueryParseError('expected operand found: {0}'.format(token))
        self.type = token.type
        self.data = token.data
        self.path = Path.fromstring(self.data) if self.type in [ Tags.EXPORT.value, Tags.PARAMETER.value ] else None

    def __eq_(self, other: Any) -> bool:
        if self.__class__ == other.__class__:
            if self.type == other.type and self.data == other.data:
                return True
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        if self.type == Tags.EXPORT.value:
            return 'exports:{0}'.format(self.data)
        elif self.type == Tags.PARAMETER.value:
            return 'parameters:{0}'.format(self.data)
        else:
            return str(self.data)

    def __repr__(self) -> str:
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    @property
    def exports(self) -> set[Path]:
        if self.type == Tags.EXPORT.value:
            return { Path.fromstring(self.data) }
        return set()

    @property
    def references(self) -> set[Path]:
        if self.type == Tags.PARAMETER.value:
            return { Path.fromstring(self.data) }
        return set()
