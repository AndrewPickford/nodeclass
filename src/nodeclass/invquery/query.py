from abc import ABC, abstractmethod, abstractproperty
from ..item.scalar import Scalar
from ..utils.url import PseudoUrl
from ..value.dictionary import Dictionary
from ..value.plain import Plain
from ..value.vlist import VList
from .exceptions import InventoryQueryParseError
from .iftest import IfTest
from .operand import OperandPathed
from .tokenizer import Tag

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, List, Set, Union
    from ..interpolator.inventory import InventoryDict, InventoryResult
    from ..utils.path import Path
    from ..value.hierarchy import Hierarchy
    from .tokenizer import Token


class QueryOptions:
    def __init__(self):
        self.all_envs = False
        self.ignore_errors = False

    def set(self, opt: 'str'):
        if opt == '+allenvs':
            self.all_envs = True
        elif opt == '+ignoreerrors':
            self.ignore_errors = True

class Query(ABC):
    def __init__(self, options: 'QueryOptions'):
        self.all_envs = options.all_envs
        self.ignore_errors = options.ignore_errors

    def __eq_(self, other: 'Any') -> 'bool':
        if self.__class__ == other.__class__:
            if (self.all_envs, self.ignore_errors) == (other.all_envs, other.ignore_errors):
                return True
        return False

    def __hash__(self) -> 'int':
        return hash(str(self))

    @abstractmethod
    def __str__(self) -> 'str':
        pass

    def options_str(self) -> 'str':
        opts = []
        if self.all_envs:
            opts.append('+AllEnvs')
        if self.ignore_errors:
            opts.append('+IgnoreErrors')
        string = ' '.join(opts)
        if len(string) > 0:
            string += ' '
        return string

    def _common_evaluate_checks(self, node: 'InventoryResult', environment: 'str') -> 'bool':
        # The node must be in the same environment or the +AllEnvs option is set
        if node.environment != environment and self.all_envs == False:
            return False
        # In the case of queries with the +IgnoreErrors when the required paths in the node exports
        # cannot be evaluated the query is added to the set of failed queries for the node.
        # Fail the check if the query is on the list of failed_queries
        if self in node.failed_queries:
            return False
        return True

    @abstractproperty
    def exports(self) -> 'Set[Path]':
        pass

    @abstractproperty
    def references(self) -> 'Set[Path]':
        pass

    @abstractmethod
    def evaluate(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Union[Dictionary, VList]':
        pass


class IfQuery(Query):
    def __init__(self, tokens: 'List[Token]', options: 'QueryOptions'):
        super().__init__(options)
        if tokens[0].type != Tag.EXPORT.value:
            raise InventoryQueryParseError('if queries begin with an export to return, found {0}'.format(tokens[0]))
        if tokens[1].type != Tag.IF.value:
            raise InventoryQueryParseError('if queries begin with an export followed by "if", found {0}'.format(tokens[1]))
        self.returned = OperandPathed(tokens[0])
        self.test = IfTest(tokens[2:])

    def __eq_(self, other: 'Any') -> 'bool':
        if self.__class__ == other.__class__:
            if (self.returned, self.test) == (other.returned, other.test):
                return super().__eq__(other)
        return False

    def __ne__(self, other: 'Any') -> 'bool':
        return not self.__eq__(other)

    def __str__(self) -> 'str':
        return '{0}{1} if {2}'.format(self.options_str(), self.returned, self.test)

    def __repr__(self) -> 'str':
        return '{0}({1}{2} if {3})'.format(self.__class__.__name__, self.options_str(), repr(self.returned), repr(self.test))

    def evaluate(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Dictionary':
        answer = {}
        for name, node in inventory.items():
            if self._common_evaluate_checks(node, environment):
                if self.returned.path in node.exports:
                    if self.test.evaluate(node.exports, context):
                        answer[name] = node.exports[self.returned.path]
        return Dictionary(answer, PseudoUrl('invquery', 'invquery'), check_for_prefix=False)

    @property
    def exports(self) -> 'Set[Path]':
        return self.returned.exports | self.test.exports

    @property
    def references(self) -> 'Set[Path]':
        return self.returned.references | self.test.references


class ListIfQuery(Query):
    def __init__(self, tokens: 'List[Token]', options: 'QueryOptions'):
        super().__init__(options)
        if tokens[0].type != Tag.IF.value:
            raise InventoryQueryParseError('list if queries begin with "if", found {0}'.format(tokens[0]))
        self.test = IfTest(tokens[1:])

    def __eq_(self, other: 'Any') -> 'bool':
        if self.__class__ == other.__class__:
            if self.test == other.test:
                return super().__eq__(other)
        return False

    def __ne__(self, other: 'Any') -> 'bool':
        return not self.__eq__(other)

    def __str__(self) -> 'str':
        return '{0}if {1}'.format(self.options_str(), self.test)

    def __repr__(self) -> 'str':
        return '{0}({1}if {2})'.format(self.__class__.__name__, self.options_str(), repr(self.test))

    def evaluate(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'VList':
        answer = []
        for name, node in inventory.items():
            if self._common_evaluate_checks(node, environment):
                if self.test.evaluate(node.exports, context):
                    answer.append(Plain(Scalar(name), PseudoUrl('invquery', 'invquery')))
        return VList(answer, PseudoUrl('invquery', 'invquery'))

    @property
    def exports(self) -> 'Set[Path]':
        return self.test.exports

    @property
    def references(self) -> 'Set[Path]':
        return self.test.references


class ValueQuery(Query):
    def __init__(self, tokens: 'List[Token]', options: 'QueryOptions'):
        super().__init__(options)
        if tokens[0].type != Tag.EXPORT.value or len(tokens) > 1:
            raise InventoryQueryParseError('value queries consist of an export to return, found: {0}'.format(tokens))
        self.returned = OperandPathed(tokens[0])

    def __eq_(self, other: 'Any') -> 'bool':
        if self.__class__ == other.__class__:
            if self.returned == other.returned:
                return super().__eq__(other)
        return False

    def __ne__(self, other: 'Any') -> 'bool':
        return not self.__eq__(other)

    def __str__(self) -> 'str':
        return '{0}{1}'.format(self.options_str(), self.returned)

    def evaluate(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Dictionary':
        answer = {}
        for name, node in inventory.items():
            if self._common_evaluate_checks(node, environment):
                if self.returned.path in node.exports:
                    answer[name] = node.exports[self.returned.path]
        return Dictionary(answer, PseudoUrl('invquery', 'invquery'), check_for_prefix=False)

    @property
    def exports(self) -> 'Set[Path]':
        return self.returned.exports

    @property
    def references(self) -> 'Set[Path]':
        return set()
