from .exceptions import MergeTypeError
from .merged import Merged
from .value import Value


class Dictionary(Value):
    '''
    '''

    def __init__(self, input, uri, create_func):
        super().__init__(Value.DICTIONARY, uri)
        self._dictionary = { k: create_func(v, uri) for k, v in input.items() }

    def merge(self, other):
        if other.type == Value.DICTIONARY:
            # merge other Dictionary into this one
            for k, v in other._dictionary.items():
                if k in self._dictionary:
                    self._dictionary[k] = self._dictionary[k].merge(v)
                else:
                    self._dictionary[k] = v
            return self
        elif other.type == Value.PLAIN:
            # if the Plain value is complex return a Merged object for later
            # interpolation, otherwise raise an error
            if other.complex:
                return Merged(self, other)
            else:
                raise MergeTypeError(self, other)
        elif other.type == Value.MERGE:
            return other.merge_under(other)
        else:
            raise MergeTypeError(self, other)

    def render(self):
        return { k: v.render() for k, v in self._dictionary.items() }

    def __str__(self):
        return '({0}; {1})'.format(str(self._dictionary), str(self.uri))

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self._dictionary), repr(self.uri))
