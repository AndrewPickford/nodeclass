from abc import ABC, abstractmethod
from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    try:
        # Python 3.10 and above
        from typing import TypeGuard
    except ImportError:
        from typing_extensions import TypeGuard
    from typing import List, Set, Union
    from ..interpolator.inventory import InventoryDict
    from ..invquery.query import Query
    from ..item.item import Item
    from ..utils.path import Path
    from ..utils.url import Url
    from .dictionary import Dictionary
    from .hierarchy import Hierarchy
    from .merged import Merged
    from .plain import Plain
    from .vlist import VList


class ValueType(Enum):
    PLAIN = 0
    DICTIONARY = 1
    LIST = 2
    MERGED = 3

    # Type checking helper classes (PEP 647 - User-Defined Type Guards)
    @classmethod
    def is_dictionary(cls, value: 'Value') -> 'TypeGuard[Dictionary]':
        return value.type == cls.DICTIONARY

    @classmethod
    def is_list(cls, value: 'Value') -> 'TypeGuard[VList]':
        return value.type == cls.LIST

    @classmethod
    def is_merged(cls, value: 'Value') -> 'TypeGuard[Merged]':
        return value.type == cls.MERGED

    @classmethod
    def is_plain(cls, value: 'Value') -> 'TypeGuard[Plain]':
        return value.type == cls.PLAIN

    @classmethod
    def is_renderable(cls, value: 'Value') -> 'TypeGuard[Union[Dictionary, VList, Plain]]':
        return value.type != cls.MERGED


class Value(ABC):
    '''
    '''

    __slots__ = ('copy_on_change', 'url')

    def __init__(self, url: 'Url', copy_on_change: 'bool'):
        self.url = url
        self.copy_on_change = copy_on_change

    @property
    def references(self) -> 'Set[Path]':
        '''
        Return a set of the references needed by this Value alone, excluding
        any references required by contained values.
        '''
        return set()

    @property
    def unresolved(self) -> 'bool':
        '''
        Returns True if the Value requires any references, else returns False
        '''
        return False

    def inventory_queries(self) -> 'Set[Query]':
        '''
        Return a set of all the inventory queries in this Value and any contained Values.
        '''
        return set()

    def unresolved_paths(self, path: 'Path') -> 'Set[Path]':
        '''
        Return a set of all the paths in this Value and any contained Values
        that have references.

        path: Path prefix
        '''
        return set()

    @abstractmethod
    def description(self) -> 'str':
        pass

    @abstractmethod
    def find_matching_contents_path(self, contents: 'Item') -> 'Union[None, List[str]]':
        pass

    @abstractmethod
    def merge(self, other: 'Value'):
        '''
        Merge a Value onto another Value in preparation for interpolation.
        Potentially changes the current object, this depends on the type of
        objects being merged.
        May return self or a different Value object.

        Usage:

        foo = foo.merge(bar)

        It is not allowed to merge an already merged Value onto another Value,
        for example:

        a = value.Create(dictA)
        b = value.Create(dictB)
        c = value.Create(dictC)
        d = value.Create(dictD)
        e = value.Create(dictE)

        a = a.merge(b)   #  allowed, unmerged Dictionaries b and c are merged
        a = a.merge(c)   #  onto a in turn

        d = d.merge(e)   #  allowed
        a = a.merge(d)   #  not allowed, d has already been merged with e

        other: value to merge in
        returns: merged Value object
        '''
        pass

    @abstractmethod
    def resolve(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Value':
        '''
        '''
        pass

    @abstractmethod
    def set_copy_on_change(self):
        '''
        Set the copy on change flag on this Value and any Values this value contains.
        Changes to this value will then copy the value, change the copy and return
        the changed copy.
        '''
        pass

    @property
    @abstractmethod
    def type(self) -> 'ValueType':
        pass
