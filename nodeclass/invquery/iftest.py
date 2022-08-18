from .conditional import Conditional
from .logical import Logical

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, List, Set
    from ..utils.path import Path
    from ..value.hierarchy import Hierarchy
    from .tokenizer import Token


class IfTest:
    def __init__(self, tokens: 'List[Token]'):
        self.conditionals = []
        self.logicals = []
        pos = 0
        while pos < len(tokens):
            conditional = Conditional(tokens[pos], tokens[pos+1], tokens[pos+2])
            self.conditionals.append(conditional)
            pos += 3
            if pos < len(tokens):
                self.logicals.append(Logical(tokens[pos]))
            pos += 1

    def __eq_(self, other: 'Any') -> 'bool':
        if self.__class__ == other.__class__:
            if self.conditionals == other.conditionals and self.logicals == other.logicals:
                return True
        return False

    def __ne__(self, other: 'Any') -> 'bool':
        return not self.__eq__(other)

    def __str__(self) -> 'str':
        if len(self.conditionals) == 1:
            return str(self.conditionals[0])
        result = [ str(self.conditionals[0]) ]
        for i, logical in enumerate(self.logicals):
            result.append(str(logical))
            result.append(str(self.conditionals[i+1]))
        return ' '.join(result)

    def __repr__(self) -> 'str':
        return '{0}({1})'.format(self.__class__.__name__, repr(self.conditionals))

    def evaluate(self, node_exports: 'Hierarchy', context: 'Hierarchy') -> 'bool':
        if len(self.conditionals) == 1:
            return self.conditionals[0].evaluate(node_exports, context)
        result = self.conditionals[0].evaluate(node_exports, context)
        for i, logical in enumerate(self.logicals):
            result = logical.combine(result, self.conditionals[i+1].evaluate(node_exports, context))
        return result

    @property
    def exports(self) -> 'Set[Path]':
        result = set()
        for conditional in self.conditionals:
            result |= conditional.exports
        return result

    @property
    def references(self) -> 'Set[Path]':
        result = set()
        for conditional in self.conditionals:
            result |= conditional.references
        return result
