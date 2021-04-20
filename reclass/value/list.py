from .exceptions import MergeTypeError
from .value import Value

class List(Value):
    '''
    '''
    type = Value.LIST

    def __init__(self, input, uri, create_func):
        super().__init__(uri)
        self._list = [ create_func(i, uri) for i in input ]

    def __getitem__(self, path):
        return self.getsubitem(path, 0)

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self._list), repr(self.uri))

    def __setitem__(self, path, value):
        self.setsubitem(path, 0, value)

    def __str__(self):
        return '({0}; {1})'.format(str(self._list), str(self.uri))

    def getsubitem(self, path, depth):
        if depth < path.last:
            return self._list[path[depth]][path, depth+1]
        else:
            return self._list[path[depth]]

    def setsubitem(self, path, depth, value):
        if depth < path.last:
            self._list[path[depth]][path, depth+1, value]
        else:
            self._list[path[depth]] = value

    def unresolved_paths(self, path):
        paths = set()
        for k, v in enumerate(self._list):
            paths.update(v.unresolved_paths(path.subpath(k)))
        return paths

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
        else:
            raise MergeTypeError(self, other)

    def render_all(self):
        '''
        Return a new list containing the renders of all Values in this List
        '''
        return [ i.render_all() for i in self._list ]
