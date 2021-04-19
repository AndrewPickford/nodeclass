from reclass.settings import SETTINGS
from .exceptions import MergeOverImmutableError, MergeTypeError
from .merged import Merged
from .value import Value


class Dictionary(Value):
    '''
    Wrap a dict object

    In the input dictionary keys starting with SETTINGS.overwrite_prefix ('~') will
    always overwrite when merging. Keys starting SETTINGS.immutable_prefix ('=') will
    raise an error if a merge happens with that key.
    '''
    type = Value.DICTIONARY

    def __init__(self, input, uri, create_func):
        super().__init__(uri, True)
        self._dictionary = dict()
        self._immutables = set()
        self._overwrites = set()
        for k, v in input.items():
            if k[0] == SETTINGS.overwrite_prefix:
                k = k[1:]
                self._overwrites.add(k)
            elif k[0] == SETTINGS.immutable_prefix:
                k = k[1:]
                self._immutables.add(k)
            self._dictionary[k] = create_func(v, uri)

    def __getitem__(self, path):
        return self.getsubitem(path, 0)

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self._dictionary), repr(self.uri))

    def __setitem__(self, path, value):
        self.setsubitem(path, 0, value)

    def __str__(self):
        return '({0}; {1})'.format(str(self._dictionary), str(self.uri))

    def getsubitem(self, path, depth):
        if self._dictionary[path[depth]].iterable:
            return self._dictionary[path[depth]].getsubitem(path, depth+1)
        else:
            return self._dictionary[path[depth]]

    def setsubitem(self, path, depth, value):
        if self._dictionary[path[depth]].iterable:
            self._dictionary[path[depth]].setsubitem(path, depth+1, value)
        else:
            self._dictionary[path[depth]] = value

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
                        # raise an error if a key is present in both the current and other
                        # object and the key in the current object is marked as immutable
                        raise MergeOverImmutableError(self, other)
                    if k in other._overwrites:
                        # if the key in the other dictionary is marked as an overwrite just
                        # replace the value instead of merging
                        self._dictionary[k] = v
                    else:
                        self._dictionary[k] = self._dictionary[k].merge(v)
                else:
                    self._dictionary[k] = v
            return self
        elif other.type == Value.PLAIN:
            # if the Plain value is unresolved return a Merged object for later
            # interpolation, otherwise raise an error
            if other.unresolved():
                return Merged(self, other)
            else:
                raise MergeTypeError(self, other)
        else:
            raise MergeTypeError(self, other)

    def render(self):
        '''
        Return a new dict containing the renders of all Values in this Dictionary
        '''
        return { k: v.render() for k, v in self._dictionary.items() }
