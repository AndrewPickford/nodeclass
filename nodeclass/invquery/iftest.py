from .conditional import Conditional
from .logical import Logical

class IfTest:
    def __init__(self, tokens):
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

    def __eq_(self, other):
        if self.__class__ == other.__class__:
            if self.conditionals == other.conditionals and self.logicals == other.logicals:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if len(self.conditionals) == 1:
            return str(self.conditionals[0])
        result = [ str(self.conditionals[0]) ]
        for i, logical in enumerate(self.logicals):
            result.append(str(logical))
            result.append(str(self.conditionals[i+1]))
        return ' '.join(result)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, repr(self.conditionals))

    def evaluate(self, node_exports, context):
        if len(self.conditionals) == 1:
            return self.conditionals[0].evaluate(node_exports, context)
        result = self.conditionals[0].evaluate(node_exports, context)
        for i, logical in enumerate(self.logicals):
            result = logical.combine(result, self.conditionals[i+1].evaluate(node_exports, context))
        return result

    @property
    def exports(self):
        result = set()
        for conditional in self.conditionals:
            result |= conditional.exports
        return result

    @property
    def references(self):
        result = set()
        for conditional in self.conditionals:
            result |= conditional.references
        return result
