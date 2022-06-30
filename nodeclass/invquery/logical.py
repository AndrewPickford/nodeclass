from __future__ import annotations
from typing import TYPE_CHECKING

import operator
from .exceptions import InventoryQueryParseError
from .tokenizer import Tags

if TYPE_CHECKING:
    from typing import Any
    from .tokenizer import Token


class Logical:
    def __init__(self, token: Token):
        if token.type != Tags.LOGICAL.value:
            raise InventoryQueryParseError('expected a logical operator, found: {0}'.format(token))
        data = token.data.lower()
        if data == 'or':
            self.op = operator.or_
        elif data == 'and':
            self.op = operator.and_
        else:
            raise InventoryQueryParseError('error parsing logical: {0}'.format(token))

    def __eq_(self, other: Any) -> bool:
        if self.__class__ == other.__class__:
            if self.op == other.op:
                return True
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return 'or' if self.op == operator.or_ else 'and'

    def __repr__(self) -> str:
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    def combine(self, lhs: bool, rhs: bool) -> bool:
        return self.op(lhs, rhs)
