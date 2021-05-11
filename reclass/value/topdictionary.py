from ..item.parser import parse as parse_item
from ..item.scalar import Scalar
from ..utils.path import Path
from .dictionary import Dictionary
from .exceptions import FrozenError, MergeTypeError
from .list import List
from .plain import Plain
from .value import Value


class TopDictionary:
    ''' The top level interface to nested group of dictionaries
    '''

    __slots__ = ('_dictionary', 'frozen', 'url')

    type = Value.TOP_DICTIONARY

    @staticmethod
    def from_dict(dictionary, url):
        def process_dictionary(input, url):
            return Dictionary({ k: process(v, url) for k, v in input.items() }, url)

        def process_list(input, url):
            return List([ process(v, url) for v in input ], url)

        def process_plain(input, url):
            if isinstance(input, str):
                item = parse_item(input)
            else:
                item = Scalar(input)
            return Plain(item, url)

        def process(input, url):
            if isinstance(input, dict):
                return process_dictionary(input, url)
            elif isinstance(input, list):
                return process_list(input, url)
            else:
                return process_plain(input, url)

        return TopDictionary({ k: process(v, url) for k, v in dictionary.items() }, url)

    def __init__(self, input, url, frozen=True):
        self._dictionary = Dictionary(input, url)
        self.url = url
        self.frozen = frozen

    def __copy__(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new._dictionary = self._dictionary
        new.url = self.url
        new.frozen = False
        return new

    def __contains__(self, path):
        return self._dictionary._contains(path, 0)

    def __getitem__(self, path):
        return self._dictionary._getsubitem(path, 0)

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self._dictionary), repr(self.url))

    def __setitem__(self, path, value):
        if self.frozen:
            raise FrozenError(self.url)
        if self._dictionary._getsubitem(path, 0).copy_on_change:
            self._dictionary = self._dictionary._setsubitem_copy_on_change(path, 0, value)
        else:
            self._dictionary._setsubitem(path, 0, value)

    def __str__(self):
        return '({0}; {1})'.format(str(self._dictionary), str(self.url))

    def extract(self, paths):
        extracted = self._dictionary._extract(paths, 0)
        return type(self)(extracted._dictionary, self.url)

    def freeze(self):
        self.frozen = True
        self._dictionary.set_copy_on_change()

    def inventory_queries(self):
        return self._dictionary.inventory_queries()

    def merge(self, other):
        if self.frozen:
            raise FrozenError(self.url)
        if other.type == Value.TOP_DICTIONARY:
            self._dictionary = self._dictionary.merge(other._dictionary)
        else:
            raise MergeTypeError(self, other)

    def render_all(self):
        return self._dictionary.render_all()

    def repr_all(self):
        return self._dictionary.repr_all()

    def unresolved_ancestor(self, path):
        return self._dictionary._unresolved_ancestor(path, 0)

    def unresolved_paths(self):
        return self._dictionary.unresolved_paths(Path.empty())
