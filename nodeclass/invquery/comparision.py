from __future__ import annotations
from typing import TYPE_CHECKING

import operator
from .exceptions import InventoryQueryParseError
from .tokenizer import Tag

if TYPE_CHECKING:
    from typing import Any
    from .tokenizer import Token


class Comparision:
    def __init__(self, token: Token):
        if token.type != Tag.COMPARISION.value:
            raise InventoryQueryParseError('expected comparision operator, found: {0}'.format(token))
        if token.data == '==':
            self.op = operator.eq
        elif token.data == '!=':
            self.op = operator.ne
        else:
            raise InventoryQueryParseError('error parsing comparision: {0}'.format(token))

    def __eq_(self, other: Any) -> bool:
        if self.__class__ == other.__class__:
            if self.op == other.op:
                return True
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return '==' if self.op == operator.eq else '!='

    def __repr__(self) -> str:
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    def compare(self, lhs: Any, rhs: Any) -> bool:
        return self.op(lhs, rhs)
