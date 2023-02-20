import copy
from .exceptions import MergeIncompatibleTypes
from .value import Value, ValueType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, List, Set, Union
    from ..interpolator.inventory import InventoryDict
    from ..item.item import Item
    from ..invquery.query import Query
    from ..utils.path import Path
    from .hierarchy import Hierarchy


class Merged(Value):
    '''
    Wrap two Dictionary, List or Plain Value objects for later evaluation
    during the interpolation step.

    Use the merge method to add additional Value objects to an existing
    Merged object.
    '''

    __slots__ = ('_values')

    type = ValueType.MERGED

    def __init__(self, first: 'Value', second: 'Value', copy_on_change: 'bool' = False):
        super().__init__(url=first.url, copy_on_change=copy_on_change)
        self._values = [ first, second ]

    def __copy__(self) -> 'Merged':
        cls = self.__class__
        new = cls.__new__(cls)
        new._values = copy.copy(self._values)
        new.url = self.url
        new.copy_on_change = False
        return new

    def __eq__(self, other: 'Any') -> 'bool':
        if self.__class__ != other.__class__:
            return False
        if self._values == other._values:
            return True
        return False

    def __repr__(self) -> 'str':
        return '{0}[{1}]'.format(self.__class__.__name__, ','.join(map(repr, self._values)))

    def __str__(self) -> 'str':
        return '[{0}]'.format(','.join(map(str, self._values)))

    def _unresolved_ancestor(self, path: 'Path', depth: 'int') -> 'bool':
        return True

    @property
    def references(self) -> 'Set[Path]':
        refs = set()
        for v in self._values:
            refs |= v.references
        return refs

    @property
    def unresolved(self) -> 'bool':
        '''
        Merged Values are only created if at least one of the Values to
        be merged is unresolved
        '''
        return True

    def description(self) -> 'str':
        # Return str(self) for now, needs to be better
        return str(self)

    def find_matching_contents_path(self, contents: 'Item') -> 'Union[None, List[str]]':
        for v in self._values:
            p = v.find_matching_contents_path(contents)
            if p is not None:
                return []
        return None

    def inventory_queries(self) -> 'Set[Query]':
        queries = set()
        for v in self._values:
            queries.update(v.inventory_queries())
        return queries

    def merge(self, other: 'Value') -> 'Merged':
        '''
        Merged objects merge new objects on top by appending to the list of
        values to merge.
        Merging two Merged objects should never happen.
        '''
        if ValueType.is_merged(other):
            raise MergeIncompatibleTypes(self, other)
        merged = copy.copy(self) if self.copy_on_change else self
        merged._values.append(other)
        return merged

    def prepend(self, other: 'Value') -> 'Merged':
        merged = copy.copy(self) if self.copy_on_change else self
        merged._values.insert(0, other)
        return merged

    def repr_all(self) -> 'str':
        return repr(self)

    def resolve(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Value':
        '''
        '''
        new = copy.copy(self) if self.copy_on_change else self
        unresolved = False
        for i, v in enumerate(new._values):
            if v.unresolved:
                new._values[i] = v.resolve(context, inventory, environment)
                if new._values[i].unresolved:
                    unresolved = True
        if unresolved:
            return new
        else:
            new.set_copy_on_change()
            resolved = new._values[0]
            for v in new._values[1:]:
                resolved = resolved.merge(v)
            return resolved

    def set_copy_on_change(self):
        self.copy_on_change = True
        map(lambda x: x.set_copy_onchange(), self._values)

    def unresolved_paths(self, path: 'Path') -> 'Set[Path]':
        '''
        Merged Values always have at least one contained Item with references
        '''
        return { path }
