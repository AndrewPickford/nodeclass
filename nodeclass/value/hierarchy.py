import copy
import yaml
from ..exceptions import InterpolationError, InputError
from ..item.parser import parse as parse_item
from ..item.scalar import Scalar
from ..utils.path import Path
from .dictionary import Dictionary
from .exceptions import FrozenHierarchy, NotHierarchy
from .list import List
from .plain import Plain
from .value import Value


class Hierarchy:
    ''' The top level interface to nested group of dictionaries
    '''

    __slots__ = ('_dictionary', 'frozen', 'category', 'url')

    type = Value.HIERARCHY

    @staticmethod
    def from_dict(dictionary, url, category):
        def process(key, input, url):
            try:
                if isinstance(input, dict):
                    return Dictionary({ k: process(k, v, url) for k, v in input.items() }, url)
                elif isinstance(input, list):
                    return List([ process(i, v, url) for i, v in enumerate(input) ], url)
                else:
                    if isinstance(input, str):
                        item = parse_item(input)
                    else:
                        item = Scalar(input)
                    return Plain(item, url)
            except InputError as exception:
                exception.reverse_path.append(key)
                raise
        try:
            return Hierarchy({ k: process(k, v, url) for k, v in dictionary.items() }, url, category)
        except InputError as exception:
            exception.category = category
            exception.url = url
            raise

    @staticmethod
    def merge_multiple(hierarchies, category, helper=None):
        # Check for an empty hierarchies list. This occurs during inventory queries
        # that include nodes with no included classes.
        if len(hierarchies) == 0:
            return Hierarchy.from_dict({}, '', category)
        result = copy.copy(hierarchies[0])
        try:
            for h in hierarchies[1:]:
                result.merge(h, helper)
        except InterpolationError as exception:
            exception.category = category
            raise
        return result

    def __init__(self, input, url, category, frozen=True):
        self._dictionary = Dictionary(input, url)
        self.url = url
        self.frozen = frozen
        self.category = category

    def __copy__(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new._dictionary = self._dictionary
        new.url = self.url
        new.category = self.category
        new.frozen = False
        return new

    def __contains__(self, path):
        return self._dictionary._contains(path, 0)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        # Test if the contents, i.e. self._dictionary and other._dictionary are the same
        # ignore self.url and self.frozen
        if self._dictionary == other._dictionary:
            return True
        return False

    def __getitem__(self, path):
        try:
            return self._dictionary._getsubitem(path, 0)
        except InterpolationError as exception:
            exception.category = self.category
            raise

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self._dictionary), repr(self.url))

    def __setitem__(self, path, value):
        if self.frozen:
            raise FrozenHierarchy(self.url, self.category)
        if self._dictionary._getsubitem(path, 0).copy_on_change:
            self._dictionary = self._dictionary._setsubitem_copy_on_change(path, 0, value)
        else:
            self._dictionary._setsubitem(path, 0, value)

    def __str__(self):
        return '({0}; {1})'.format(str(self._dictionary), str(self.url))

    def set_copy_on_change(self):
        self._dictionary.set_copy_on_change()

    def extract(self, paths):
        extracted = self._dictionary._extract(paths, 0)
        return type(self)(extracted._dictionary, self.url, self.category)

    def find_matching_contents_path(self, contents):
        p = self._dictionary.find_matching_contents_path(contents)
        if p is not None:
            p.reverse()
            return Path.fromlist(p)
        return None

    def freeze(self):
        self.frozen = True
        self._dictionary.set_copy_on_change()

    def get(self, path, default):
        if path in self:
            return self[path]
        return default

    def inventory_queries(self):
        return self._dictionary.inventory_queries()

    def merge(self, other, helper=None):
        def inner():
            try:
                self._dictionary = self._dictionary.merge(other._dictionary)
            except InterpolationError as exception:
                exception.category = self.category
                raise

        if self.__class__ != other.__class__:
            raise NotHierarchy(self.url, self.category, other)
        if self.frozen:
            raise FrozenHierarchy(self.url, self.category)
        if helper:
            helper.hierarchy_merge_wrapper(self, other, inner)
        else:
            inner()

    def pprint(self):
        print('Hierarchy, category={0}, url={1}'.format(self.category, self.url))
        print(yaml.dump(self._dictionary.repr_all(), default_flow_style=False, Dumper=yaml.CSafeDumper))

    def render_all(self):
        return self._dictionary.render_all()

    def repr_all(self):
        return self._dictionary.repr_all()

    def unresolved_ancestor(self, path):
        return self._dictionary._unresolved_ancestor(path, 0)

    def unresolved_paths(self):
        return self._dictionary.unresolved_paths(Path.empty())
