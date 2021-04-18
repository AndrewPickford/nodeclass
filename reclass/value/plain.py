from .exceptions import MergeTypeError, ValueRenderUndefinedError
from .merged import Merged
from .value import Value
from .item import Scalar
from .parser import Parser


class Plain(Value):
    '''
    '''
    parser = Parser()

    def __init__(self, input, uri):
        super().__init__(Value.PLAIN, uri)
        if isinstance(input, str):
            self.item = self.parser.parse(input)
        else:
            self.item = Scalar(input)
        self.complex = self.item.complex

    @property
    def references(self):
        return self.item.references

    def merge(self, other):
        if other.type == Value.PLAIN:
            # if both Plain objects have no references just handle the merge
            # by returning the other object, otherwise return a Merged object
            # for later interpolation
            if self.complex or other.complex:
                return Merged(self, other)
            else:
                return other
        elif other.type == Value.DICTIONARY or other.type == Value.LIST:
            # if the current object is complex return a Merged object for later
            # interpolation, otherwise raise an error
            if other.complex:
                return Merge(self, other)
            else:
                raise MergeTypeError(self, other)
        elif other.type == Value.MERGE:
            return other.merge_under(self)
        else:
            raise MergeTypeError(self, other)

    def render(self):
        try:
            return self.item.render()
        except ItemRenderUndefinedError as e:
            raise ValueRenderUndefinedError(self)

    def __str__(self):
        return '({0}; {1})'.format(str(self.item), str(self.uri))

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self.item), repr(self.uri))
