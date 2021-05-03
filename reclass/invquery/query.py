from reclass.item.scalar import Scalar as BaseScalar
from reclass.value.dictionary import Dictionary as BaseDictionary
from reclass.value.list import List as BaseList
from reclass.value.plain import Plain as BasePlain
from .exceptions import InventoryQueryParseError
from .iftest import IfTest as BaseIfTest
from .operand import Operand as BaseOperand
from .parser_functions import Tags

class QueryOptions:
    def __init__(self):
        self.all_envs = False
        self.ignore_errors = False

    def set(self, opt):
        if opt == '+allenvs':
            self.all_envs = True
        elif opt == '+ignoreerrors':
            self.ignore_errors = True

class Query:
    def __init__(self, options):
        self.all_envs = options.all_envs
        self.ignore_errors = options.ignore_errors

    def __eq_(self, other):
        if self.__class__ == other.__class__:
            if (self.all_envs, self.ignore_errors) == (other.all_envs, other.ignore_errors):
                return True
        return False

    def __hash__(self):
        return hash(str(self))

    def options_str(self):
        all_envs = '+AllEnvs' if self.all_envs else ''
        ignore_errors = '+IgnoreErrors' if self.ignore_errors else ''
        string = ''.join([all_envs, ignore_errors])
        if len(string) > 0:
            string += ' '
        return string


class IfQuery(Query):
    IfTest = BaseIfTest
    Dictionary = BaseDictionary
    Operand = BaseOperand

    def __init__(self, tokens, options):
        super().__init__(options)
        if tokens[0].type != Tags.EXPORT.value:
            raise InventoryQueryParseError(tokens, 'if queries begin with an export to return')
        if tokens[1].type != Tags.IF.value:
            raise InventoryQueryParseError(tokens, 'if queries begin with start with an export followed by "if"')
        self.returned = self.Operand(tokens[0])
        self.test = self.IfTest(tokens[2], tokens[3], tokens[4])

    def __eq_(self, other):
        if self.__class__ == other.__class__:
            if (self.returned, self.test) == (other.returned, other.test):
                return super().__eq__(self, other)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '{0}{1} if {2}'.format(self.options_str(), self.returned, self.test)

    def __repr__(self):
        return '{0}({1}{2} if {3})'.format(self.__class__.__name__, self.options_str(), repr(self.returned), repr(self.test))

    def evaluate(self, context, inventory, environment):
        answer = {}
        for name, node in inventory.items():
            if node.environment == environment or self.all_envs:
                if self.returned.path in node.exports:
                    if self.test.evaluate(node.exports, context):
                        answer[name] = node.exports[self.returned.path]
        return self.Dictionary(answer, 'invquery', check_for_prefix=False)

    @property
    def exports(self):
        return self.returned.exports |self.test.exports

    @property
    def references(self):
        return self.returned.references | self.test.references


class ListIfQuery(Query):
    IfTest = BaseIfTest
    List = BaseList
    Plain = BasePlain
    Scalar = BaseScalar

    def __init__(self, tokens, options):
        super().__init__(options)
        if tokens[0].type != Tags.IF.value:
            raise InventoryQueryParseError(tokens, 'list if queries begin with "if"')
        self.test = self.IfTest(tokens[1], tokens[2], tokens[3])

    def __eq_(self, other):
        if self.__class__ == other.__class__:
            if self.test == other.test:
                return super().__eq__(self, other)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '{0}if {1}'.format(self.options_str(), self.test)

    def __repr__(self):
        return '{0}({1}if {2})'.format(self.__class__.__name__, self.options_str(), repr(self.test))

    def evaluate(self, context, inventory, environment):
        answer = []
        for name, node in inventory.items():
            if node.environment == environment or self.all_envs:
                if self.test.evaluate(node.exports, context):
                    answer.append(self.Plain(self.Scalar(name), 'invquery'))
        return self.List(answer, 'invquery')

    @property
    def exports(self):
        return self.test.exports

    @property
    def references(self):
        return self.test.references


class ValueQuery(Query):
    Dictionary = BaseDictionary
    Operand = BaseOperand

    def __init__(self, tokens, options):
        super().__init__(options)
        if tokens[0].type != Tags.EXPORT.value:
            raise InventoryQueryParseError(tokens, 'value queries begin with an export to return')
        self.returned = self.Operand(tokens[0])

    def evaluate(self, context, inventory, environment):
        answer = {}
        for name, node in inventory.items():
            if node.environment == environment or self.all_envs:
                if self.returned.path in node.exports:
                    answer[name] = node.exports[self.returned.path]
        return self.Dictionary(answer, 'invquery', check_for_prefix=False)

    @property
    def exports(self):
        return self.test.exports

    @property
    def references(self):
        return self.test.references
