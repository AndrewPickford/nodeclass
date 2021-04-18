from .exceptions import MergeTypeError
from .value import Value

class List(Value):
    '''
    '''

    def __init__(self, input, uri, create_func):
        super().__init__(Value.LIST, uri)
        self._list = [ create_func(i, uri) for i in input ]

    def merge(self, other):
        if other.type == Value.LIST:
            # merge Lists together
            self._list.extend(other._list)
            return self
        elif other.type == Value.PLAIN:
            # if the plain Value is a reference return a Merge object
            # for later interpolation, otherwise raise an error
            if other.complex:
                return Merge(self, other)
            else:
                raise MergeTypeError(self, other)
        elif other.type == Value.MERGE:
            return merge.merge_under(self)
        else:
            raise MergeTypeError(self, other)

    def render(self):
        return [ i.render() for i in self._list ]

    def __str__(self):
        return '({0}; {1})'.format(str(self._list), str(self.uri))

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self._list), repr(self.uri))
