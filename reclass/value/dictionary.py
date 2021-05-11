import copy
from collections import defaultdict
from ..context import CONTEXT
from .exceptions import MergeOverImmutableError, MergeTypeError
from .merged import Merged
from .value import Value


class Dictionary(Value):
    '''
    Wrap a dict object

    In the input dictionary keys starting with CONTEXT.settings.overwrite_prefix ('~') will
    always overwrite when merging. Keys starting CONTEXT.settings.immutable_prefix ('=') will
    raise an error if a merge happens with that key.

    All keys for items contained in a Dictionary object are converted to strings, as references
    to keys always refer to the string representation of the key.
    '''

    __slots__ = ('_dictionary', '_immutables', '_overwrites')

    type = Value.DICTIONARY

    def __init__(self, input, url, copy_on_change=True, check_for_prefix=True):
        def process_key(key):
            if not check_for_prefix:
                return key
            if key[0] == overwrite_prefix:
                key = key[1:]
                self._overwrites.add(key)
            elif key[0] == immutable_prefix:
                key = key[1:]
                self._immutables.add(key)
            return key

        super().__init__(url=url, copy_on_change=copy_on_change)
        self._immutables = set()
        self._overwrites = set()
        overwrite_prefix = CONTEXT.settings.overwrite_prefix
        immutable_prefix = CONTEXT.settings.immutable_prefix
        self._dictionary = { process_key(str(k)): v for k, v in input.items() }

    def __copy__(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new.url = self.url
        new._immutables = copy.copy(self._immutables)
        new._overwrites = copy.copy(self._overwrites)
        new._dictionary = copy.copy(self._dictionary)
        new.copy_on_change = False
        return new

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self._dictionary), repr(self.url))

    def __str__(self):
        return '({0}; {1})'.format(str(self._dictionary), str(self.url))

    def _contains(self, path, depth):
        if depth < path.last:
            return self._dictionary[path[depth]]._contains(path, depth + 1)
        else:
            return path[depth] in self._dictionary

    def _extract(self, paths, depth):
        extracted = type(self)(input={}, url=self.url, copy_on_change=False)
        set_keys = set()
        descend_keys = defaultdict(set)
        for path in paths:
            if depth < path.last:
                descend_keys[path[depth]].add(path)
            else:
                set_keys.add(path[depth])
        descend_keys = { k: v for k, v in descend_keys.items() if k not in set_keys }
        for key in set_keys:
            extracted._dictionary[key] = self._dictionary[key]
        for key, key_paths in descend_keys.items():
            extracted._dictionary[key] = self._dictionary[key]._extract(key_paths, depth + 1)
        return extracted

    def _getsubitem(self, path, depth):
        if depth < path.last:
            return self._dictionary[path[depth]]._getsubitem(path, depth + 1)
        return self._dictionary[path[depth]]

    def _setsubitem(self, path, depth, value):
        if depth < path.last:
            self._dictionary[path[depth]]._setsubitem(path, depth+1, value)
        else:
            self._dictionary[path[depth]] = value

    def _setsubitem_copy_on_change(self, path, depth, value):
        new = copy.copy(self) if self.copy_on_change else self
        if depth < path.last:
            new._dictionary[path[depth]] = new._dictionary[path[depth]]._setsubitem_copy_on_change(path, depth+1, value)
        else:
            new._dictionary[path[depth]] = value
        return new

    def _unresolved_ancestor(self, path, depth):
        if depth < path.last and path[depth] in self._dictionary:
            return self._dictionary[path[depth]]._unresolved_ancestor(path, depth + 1)
        return False

    def inventory_queries(self):
        queries = set()
        for v in self._dictionary.values():
            queries.update(v.inventory_queries())
        return queries

    def merge(self, other):
        if other.type == Value.DICTIONARY:
            merged = copy.copy(self) if self.copy_on_change else self
            # merge other Dictionary into this one
            for k, v in other._dictionary.items():
                if k in merged._dictionary:
                    if k in merged._immutables:
                        # raise an error if a key is present in both dictionaries and is
                        # marked as immutable in this dictionary
                        raise MergeOverImmutableError(self, other)
                    elif k in other._overwrites:
                        # if the key in the other dictionary is marked as an overwrite just
                        # replace the value instead of merging
                        merged._dictionary[k] = v
                    else:
                        merged._dictionary[k] = merged._dictionary[k].merge(v)
                else:
                    merged._dictionary[k] = v
                merged._immutables.update(other._immutables)
            return merged
        elif other.type == Value.PLAIN:
            # if the Plain value is unresolved return a Merged object for later
            # interpolation, otherwise raise an error
            if other.unresolved:
                return Merged(self, other)
            else:
                raise MergeTypeError(self, other)
        else:
            raise MergeTypeError(self, other)

    def render_all(self):
        '''
        Return a new dict containing the renders of all Values in this Dictionary
        '''
        return { k: v.render_all() for k, v in self._dictionary.items() }

    def repr_all(self):
        return { k: v.repr_all() for k, v in self._dictionary.items() }

    def set_copy_on_change(self):
        self.copy_on_change = True
        for v in self._dictionary.values():
            v.set_copy_on_change()

    def unresolved_paths(self, path):
        paths = set()
        for k, v in self._dictionary.items():
            paths.update(v.unresolved_paths(path.subpath(k)))
        return paths
