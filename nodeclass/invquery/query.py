from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod, abstractproperty
from ..item.scalar import Scalar
from ..value.dictionary import Dictionary
from ..value.list import List
from ..value.plain import Plain
from .exceptions import InventoryQueryParseError
from .iftest import IfTest
from .operand import Operand
from .tokenizer import Tag

if TYPE_CHECKING:
    from typing import Any
    from ..interpolator.inventory import InventoryDict
    from ..utils.path import Path
    from ..value.hierarchy import Hierarchy
    from .tokenizer import Token


class QueryOptions:
    def __init__(self):
        self.all_envs = False
        self.ignore_errors = False

    def set(self, opt: str):
        if opt == '+allenvs':
            self.all_envs = True
        elif opt == '+ignoreerrors':
            self.ignore_errors = True

class Query(ABC):
    def __init__(self, options: QueryOptions):
        self.all_envs = options.all_envs
        self.ignore_errors = options.ignore_errors

    def __eq_(self, other: Any) -> bool:
        if self.__class__ == other.__class__:
            if (self.all_envs, self.ignore_errors) == (other.all_envs, other.ignore_errors):
                return True
        return False

    def __hash__(self) -> int:
        return hash(str(self))

    def options_str(self) -> str:
        opts = []
        if self.all_envs:
            opts.append('+AllEnvs')
        if self.ignore_errors:
            opts.append('+IgnoreErrors')
        string = ' '.join(opts)
        if len(string) > 0:
            string += ' '
        return string

    @abstractproperty
    def exports(self) -> set[Path]:
        pass

    @abstractproperty
    def references(self) -> set[Path]:
        pass

    @abstractmethod
    def evaluate(self, context: Hierarchy, inventory: InventoryDict, environment: str) -> Dictionary|List:
        pass


class IfQuery(Query):
    def __init__(self, tokens: list[Token], options: QueryOptions):
        super().__init__(options)
        if tokens[0].type != Tag.EXPORT.value:
            raise InventoryQueryParseError('if queries begin with an export to return, found {0}'.format(tokens[0]))
        if tokens[1].type != Tag.IF.value:
            raise InventoryQueryParseError('if queries begin with an export followed by "if", found {0}'.format(tokens[1]))
        self.returned = Operand(tokens[0])
        self.test = IfTest(tokens[2:])

    def __eq_(self, other: Any) -> bool:
        if self.__class__ == other.__class__:
            if (self.returned, self.test) == (other.returned, other.test):
                return super().__eq__(other)
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return '{0}{1} if {2}'.format(self.options_str(), self.returned, self.test)

    def __repr__(self) -> str:
        return '{0}({1}{2} if {3})'.format(self.__class__.__name__, self.options_str(), repr(self.returned), repr(self.test))

    def evaluate(self, context: Hierarchy, inventory: InventoryDict, environment: str) -> Dictionary:
        answer = {}
        for name, node in inventory.items():
            if node.environment == environment or self.all_envs:
                if self.returned.path in node.exports:
                    if self.test.evaluate(node.exports, context):
                        answer[name] = node.exports[self.returned.path]
        return Dictionary(answer, 'invquery', check_for_prefix=False)

    @property
    def exports(self) -> set[Path]:
        return self.returned.exports | self.test.exports

    @property
    def references(self) -> set[Path]:
        return self.returned.references | self.test.references


class ListIfQuery(Query):
    def __init__(self, tokens: list[Token], options: QueryOptions):
        super().__init__(options)
        if tokens[0].type != Tag.IF.value:
            raise InventoryQueryParseError('list if queries begin with "if", found {0}'.format(tokens[0]))
        self.test = IfTest(tokens[1:])

    def __eq_(self, other: Any) -> bool:
        if self.__class__ == other.__class__:
            if self.test == other.test:
                return super().__eq__(other)
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return '{0}if {1}'.format(self.options_str(), self.test)

    def __repr__(self) -> str:
        return '{0}({1}if {2})'.format(self.__class__.__name__, self.options_str(), repr(self.test))

    def evaluate(self, context: Hierarchy, inventory: InventoryDict, environment: str) -> List:
        answer = []
        for name, node in inventory.items():
            if node.environment == environment or self.all_envs:
                if self.test.evaluate(node.exports, context):
                    answer.append(Plain(Scalar(name), 'invquery'))
        return List(answer, 'invquery')

    @property
    def exports(self) -> set[Path]:
        return self.test.exports

    @property
    def references(self) -> set[Path]:
        return self.test.references


class ValueQuery(Query):
    def __init__(self, tokens: list[Token], options: QueryOptions):
        super().__init__(options)
        if tokens[0].type != Tag.EXPORT.value or len(tokens) > 1:
            raise InventoryQueryParseError('value queries consist of an export to return, found: {0}'.format(tokens))
        self.returned = Operand(tokens[0])

    def evaluate(self, context: Hierarchy, inventory: InventoryDict, environment: str) -> Dictionary:
        answer = {}
        for name, node in inventory.items():
            if node.environment == environment or self.all_envs:
                if self.returned.path in node.exports:
                    answer[name] = node.exports[self.returned.path]
        return Dictionary(answer, 'invquery', check_for_prefix=False)

    @property
    def exports(self) -> set[Path]:
        return self.returned.exports

    @property
    def references(self) -> set[Path]:
        return set()
