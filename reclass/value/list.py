import copy
from .exceptions import MergeTypeError
from .merged import Merged as BaseMerged
from .value import Value

class List(Value):
    '''
    '''
    type = Value.LIST
    Merged = BaseMerged

    def __init__(self, input, url, copy_on_change=True):
        super().__init__(url=url, copy_on_change=copy_on_change)
        self._list = input

    def __copy__(self):
        c = type(self)([], self.url, copy_on_change=False)
        c._list = copy.copy(self._list)
        return c

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self._list), repr(self.url))

    def __str__(self):
        return '({0}; {1})'.format(str(self._list), str(self.url))

    def _getsubitem(self, path, depth):
        if depth < path.last:
            return self._list[path[depth]]._getsubitem(path, depth+1)
        else:
            return self._list[path[depth]]

    def _setsubitem(self, path, depth, value):
        if depth < path.last:
            self._list[path[depth]]._setsubitem(path, depth+1, value)
        else:
            self._list[path[depth]] = value

    def _setsubitem_copy_on_change(self, path, depth, value):
        new = copy.copy(self) if self.copy_on_change else self
        if depth < path.last:
            new._list[path[depth]] = new._list[path[depth]]._setsubitem_copy_on_change(path, depth+1, value)
        else:
            new._list[path[depth]] = value
        return new

    def _unresolved_ancestor(self, path, depth):
        if depth < path.last:
            return self._list[path[depth]]._unresolved_ancestor(path, depth + 1)
        elif path[depth] < len(self._list):
            return False
        raise KeyError('{0} not present'.format(str(path)))

    def unresolved_ancestor(self, path):
        return self._unresolved_ancestor(path, 0)

    def inventory_queries(self):
        queries = set()
        for v in self._list:
            queries.update(v.inventory_queries())
        return queries

    def unresolved_paths(self, path):
        paths = set()
        for k, v in enumerate(self._list):
            paths.update(v.unresolved_paths(path.subpath(k)))
        return paths

    def set_copy_on_change(self):
        self.copy_on_change = True
        for v in self._list:
            v.set_copy_on_change()

    def merge(self, other):
        if other.type == Value.LIST:
            merged = copy.copy(self) if self.copy_on_change else self
            # merge Lists together
            merged._list.extend(other._list)
            return merged
        elif other.type == Value.PLAIN:
            # if the plain Value is a reference return a Merge object
            # for later interpolation, otherwise raise an error
            if other.unresolved:
                return self.Merged(self, other)
            else:
                raise MergeTypeError(self, other)
        else:
            raise MergeTypeError(self, other)

    def render_all(self):
        '''
        Return a new list containing the renders of all Values in this List
        '''
        return [ i.render_all() for i in self._list ]
