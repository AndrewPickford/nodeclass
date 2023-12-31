from ..context import CONTEXT
from .exceptions import MergeIncompatibleTypes
from .merged import Merged
from .value import Value, ValueType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, List, Set, Union
    from ..interpolator.inventory import InventoryDict
    from ..invquery.query import Query
    from ..item.item import Item, RenderableValue
    from ..utils.path import Path
    from ..utils.url import Url
    from .hierarchy import Hierarchy


class Plain(Value):
    '''
    '''

    __slots__ = ('item')

    type = ValueType.PLAIN

    def __init__(self, item: 'Item', url: 'Url', copy_on_change: 'bool' = True):
        super().__init__(url=url, copy_on_change=copy_on_change)
        self.item = item

    def __copy__(self) -> 'Plain':
        return type(self)(self.item, self.url, copy_on_change=False)

    def __eq__(self, other: 'Any') -> 'bool':
        if self.__class__ != other.__class__:
            return False
        if self.item == other.item:
            return True
        return False

    def __repr__(self) -> 'str':
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self.item), repr(self.url))

    def __str__(self) -> 'str':
        return '({0}; {1})'.format(str(self.item), str(self.url))

    def _unresolved_ancestor(self, path: 'List[int]', depth: 'int'):
        return True

    @property
    def references(self) -> 'Set[Path]':
        return self.item.references

    @property
    def unresolved(self) -> 'bool':
        return self.item.unresolved

    def description(self) -> 'str':
        return self.item.description()

    def find_matching_contents_path(self, contents: 'Item') -> 'Union[None, List[str]]':
        if self.item.contents is contents:
            return []
        return None

    def inventory_queries(self) -> 'Set[Query]':
        query = self.item.inventory_query
        if query is None:
            return set()
        return { query }

    def merge(self, other: 'Value') -> 'Value':
        if other.type == ValueType.PLAIN:
            # if both Plain objects have no references handle the merge now
            # by returning the other object, otherwise return a Merged object
            # for later interpolation
            if self.unresolved or other.unresolved:
                return Merged(self, other)
            else:
                return other
        elif other.type == ValueType.DICTIONARY or other.type == ValueType.LIST:
            # if the current object is unresolved return a Merged object for later
            # interpolation
            if self.unresolved:
                return Merged(self, other)
            elif self.item.contents is None and CONTEXT.settings.allow_none_overwrite:
                return other
                raise MergeIncompatibleTypes(self, other)
        elif ValueType.is_merged(other):
            return other.prepend(self)
        raise MergeIncompatibleTypes(self, other)

    def resolve(self, context: 'Hierarchy', inventory: 'InventoryDict', environment: 'str') -> 'Value':
        '''
        Step through one level of indirection.

        First see if the item we have can resolve to an already existing Value in the
        context dictionary. For example if the Item we have is a simple reference, ${foo}.
        If this is the case return the referenced Value.

        If not use resolve_to_item to return a new item which has removed a level
        of indirection. Then either return a new Plain value containing the new item
        or set self.item to the new item and return self, depending on if copy_on_change
        is set.
        '''
        value = self.item.resolve_to_value(context, inventory, environment)
        if value is None:
            if self.copy_on_change:
                return type(self)(self.item.resolve_to_item(context, inventory, environment), self.url)
            else:
                self.item = self.item.resolve_to_item(context, inventory, environment)
                return self
        else:
            value.set_copy_on_change()
            return value

    def render(self) -> 'RenderableValue':
        '''
        Return a render of the underlying Item in this Value
        '''
        return self.item.render()

    def render_all(self) -> 'RenderableValue':
        return self.render()

    def repr_all(self) -> 'str':
        return repr(self)

    def resolved_paths(self, path: 'Path') -> 'Set[Path]':
        if self.item.unresolved:
            return set()
        else:
            return { path }

    def set_copy_on_change(self):
        self.copy_on_change = True

    def unresolved_paths(self, path: 'Path') -> 'Set[Path]':
        if self.item.unresolved:
            return { path }
        else:
            return set()
