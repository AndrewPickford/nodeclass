import copy
from .exceptions import MergeOverImmutableError, MergeTypeError
from .merged import Merged as BaseMerged
from .value import Value


class Dictionary(Value):
    '''
    Wrap a dict object

    In the input dictionary keys starting with self.settings.overwrite_prefix ('~') will
    always overwrite when merging. Keys starting self.settings.immutable_prefix ('=') will
    raise an error if a merge happens with that key.
    '''
    type = Value.DICTIONARY
    Merged = BaseMerged

    def __init__(self, input, url):
        def process_key(key):
            if key[0] == self.settings.overwrite_prefix:
                key = key[1:]
                self._overwrites.add(key)
            elif key[0] == self.settings.immutable_prefix:
                key = key[1:]
                self._immutables.add(key)
            return key

        super().__init__(url)
        self._immutables = set()
        self._overwrites = set()
        self._dictionary = { process_key(k): v for k, v in input.items() }

    def __copy__(self):
        c = type(self)({}, self.url)
        c._immutables = copy.copy(self._immutables)
        c._overwrites = copy.copy(self._overwrites)
        c._dictionary = { k: copy.copy(v) for k, v in self._dictionary.items() }
        return c

    def __getitem__(self, path):
        return self._getsubitem(path, 0)

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self._dictionary), repr(self.url))

    def __setitem__(self, path, value):
        self._setsubitem(path, 0, value)

    def __str__(self):
        return '({0}; {1})'.format(str(self._dictionary), str(self.url))

    def _getsubitem(self, path, depth):
        if depth < path.last:
            return self._dictionary[path[depth]]._getsubitem(path, depth + 1)
        else:
            return self._dictionary[path[depth]]

    def _setsubitem(self, path, depth, value):
        if depth < path.last:
            self._dictionary[path[depth]]._setsubitem(path, depth+1, value)
        else:
            self._dictionary[path[depth]] = value

    def _unresolved_ancestor(self, path, depth):
        if depth < path.last:
            return self._dictionary[path[depth]]._unresolved_ancestor(path, depth + 1)
        elif path[depth] in self._dictionary:
            return False
        raise KeyError('{0} not present'.format(str(path)))

    def unresolved_ancestor(self, path):
        return self._unresolved_ancestor(path, 0)

    def unresolved_paths(self, path):
        paths = set()
        for k, v in self._dictionary.items():
            paths.update(v.unresolved_paths(path.subpath(k)))
        return paths

    def merge(self, other):
        if other.type == Value.DICTIONARY:
            # merge other Dictionary into this one
            for k, v in other._dictionary.items():
                if k in self._dictionary:
                    if k in self._immutables:
                        # raise an error if a key is present in both dictionaries and is
                        # marked as immutable in this dictionary
                        # NOTE: What to do if the key is marked as immutable in the other
                        # dictionary?
                        raise MergeOverImmutableError(self, other)
                    elif k in other._overwrites:
                        # if the key in the other dictionary is marked as an overwrite just
                        # replace the value instead of merging
                        self._dictionary[k] = v
                    else:
                        self._dictionary[k] = self._dictionary[k].merge(v)
                else:
                    self._dictionary[k] = v
                self._immutables.update(other._immutables)
            return self
        elif other.type == Value.PLAIN:
            # if the Plain value is unresolved return a Merged object for later
            # interpolation, otherwise raise an error
            if other.unresolved:
                return self.Merged(self, other)
            else:
                raise MergeTypeError(self, other)
        else:
            raise MergeTypeError(self, other)

    def render_all(self):
        '''
        Return a new dict containing the renders of all Values in this Dictionary
        '''
        return { k: v.render_all() for k, v in self._dictionary.items() }
