from .exceptions import MergeTypeError
from .merged import Merged
from .value import Value
from .item import Scalar
from .parser import Parser


class Plain(Value):
    '''
    '''
    parser = Parser()
    type = Value.PLAIN

    def __init__(self, input, uri):
        super().__init__(uri, False)
        if isinstance(input, str):
            self.item = self.parser.parse(input)
        else:
            self.item = Scalar(input)

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self.item), repr(self.uri))

    def __str__(self):
        return '({0}; {1})'.format(str(self.item), str(self.uri))

    def unresolved(self):
        return self.item.unresolved

    def unresolved_paths(self, path):
        if self.item.unresolved:
            return { path }
        else:
            return set()

    def references(self):
        return self.item.references()

    def merge(self, other):
        if other.type == Value.PLAIN:
            # if both Plain objects have no references just handle the merge
            # by returning the other object, otherwise return a Merged object
            # for later interpolation
            if self.item.unresolved or other.item.unresolved:
                return Merged(self, other)
            else:
                return other
        elif other.type == Value.DICTIONARY or other.type == Value.LIST:
            # if the current object is unresolved return a Merged object for later
            # interpolation, otherwise raise an error
            if other.unresolved:
                return Merge(self, other)
            else:
                raise MergeTypeError(self, other)
        else:
            raise MergeTypeError(self, other)

    def render(self):
        '''
        Return a render of the underlying Item in this Value
        '''
        return self.item.render()

    def resolve(self, context, inventory):
        return self.item.resolve(context, inventory)
