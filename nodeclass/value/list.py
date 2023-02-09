import copy
from collections import defaultdict
from .exceptions import MergeIncompatibleTypes
from .merged import Merged
from .value import Value

class List(Value):
    '''
    '''

    __slots__ = ('_list')

    type = Value.LIST

    def __init__(self, input, url, copy_on_change=True):
        super().__init__(url=url, copy_on_change=copy_on_change)
        self._list = input

    def __copy__(self):
        return type(self)(copy.copy(self._list), self.url, copy_on_change=False)

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self._list), repr(self.url))

    def __str__(self):
        return '({0}; {1})'.format(str(self._list), str(self.url))

    def _contains(self, path, depth):
        n = int(path[depth])
        if depth < path.last:
            return self._list[n]._contains(path, depth + 1)
        else:
            return n < len(self._list)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if self._list == other._list:
            return True
        return False

    def _extract(self, paths, depth):
        extracted = type(self)(input=[]*len(self._list), url=self.url, copy_on_change=False)
        set_keys = set()
        descend_keys = defaultdict(set)
        for path in paths:
            if depth < path.last:
                descend_keys[int(path[depth])].add(path)
            else:
                set_keys.add(int(path[depth]))
        for key in set_keys:
            extracted._list[key] = self._list[key]
        descend_keys = { k: v for k, v in descend_keys.items() if k not in set_keys }
        for key, key_paths in descend_keys.items():
            extracted._list[key] = self._list[key]._extract(key_paths, depth + 1)
        return extracted

    def _getsubitem(self, path, depth):
        n = int(path[depth])
        if depth < path.last:
            return self._list[n]._getsubitem(path, depth+1)
        return self._list[n]

    def _setsubitem(self, path, depth, value):
        n = int(path[depth])
        if depth < path.last:
            self._list[n]._setsubitem(path, depth+1, value)
        else:
            self._list[n] = value

    def _setsubitem_copy_on_change(self, path, depth, value):
        new = copy.copy(self) if self.copy_on_change else self
        n = int(path[depth])
        if depth < path.last:
            new._list[n] = new._list[n]._setsubitem_copy_on_change(path, depth+1, value)
        else:
            new._list[n] = value
        return new

    def _unresolved_ancestor(self, path, depth):
        n = int(path[depth])
        if depth < path.last and n < len(self._list):
            return self._list[n]._unresolved_ancestor(path, depth + 1)
        return False

    def description(self) -> 'str':
        # Return str(self) for now, needs to be better
        return str(self)

    def find_matching_contents_path(self, contents):
        for k, v in enumerate(self._list):
            p = v.find_matching_contents_path(contents)
            if p is not None:
                p.append(k)
                return p
        return None

    def inventory_queries(self):
        queries = set()
        for v in self._list:
            queries.update(v.inventory_queries())
        return queries

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
                return Merged(self, other)
            else:
                raise MergeIncompatibleTypes(self, other)
        else:
            raise MergeIncompatibleTypes(self, other)

    def render_all(self):
        '''
        Return a new list containing the renders of all Values in this List
        '''
        return [ i.render_all() for i in self._list ]

    def repr_all(self):
        return [ i.repr_all() for i in self._list ]

    def set_copy_on_change(self):
        self.copy_on_change = True
        for v in self._list:
            v.set_copy_on_change()

    def unresolved_paths(self, path):
        paths = set()
        for k, v in enumerate(self._list):
            paths.update(v.unresolved_paths(path.subpath(k)))
        return paths
