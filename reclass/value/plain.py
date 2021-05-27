from ..context import CONTEXT
from .exceptions import MergeTypeError
from .merged import Merged
from .value import Value


class Plain(Value):
    '''
    '''

    __slots__ = ('item')

    type = Value.PLAIN

    def __init__(self, item, url, copy_on_change=True):
        super().__init__(url=url, copy_on_change=copy_on_change)
        self.item = item

    def __copy__(self):
        return type(self)(self.item, self.url, copy_on_change=False)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if self.item == other.item:
            return True
        return False

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self.item), repr(self.url))

    def __str__(self):
        return '({0}; {1})'.format(str(self.item), str(self.url))

    def _unresolved_ancestor(self, path, depth):
        return True

    @property
    def references(self):
        return self.item.references

    @property
    def unresolved(self):
        return self.item.unresolved

    def inventory_queries(self):
        query = self.item.inventory_query
        if query is None:
            return set()
        return { query }

    def merge(self, other):
        if other.type == Value.PLAIN:
            # if both Plain objects have no references handle the merge now
            # by returning the other object, otherwise return a Merged object
            # for later interpolation
            if self.unresolved or other.unresolved:
                return Merged(self, other)
            else:
                return other
        elif other.type == Value.DICTIONARY or other.type == Value.LIST:
            # if the current object is unresolved return a Merged object for later
            # interpolation, otherwise raise an error
            if self.unresolved:
                return Merged(self, other)
            elif self.item.contents is None and CONTEXT.settings.allow_none_overwrite:
                return other
        raise MergeTypeError(self, other)

    def resolve(self, context, inventory, environment):
        '''
        Step through one level of indirection.

        First see if the item we have can resolve to an already existing Value in the
        context dictionary. For example if the Item we have is a simple reference, ${foo}.
        If this is the case return the referenced Value.

        If not use resolve_to_item to return a new item which has removed a level
        of indirection. Then either return a new Plain value containing the new item
        or set self.item to the new item and return self, depending on if copy_on_change
        is set.

        context: Dictionary of resolved parameter values
        inventory: Dictionary of required inventory query answers
        environment: Environment to evaluate inventory queries
        returns: resolved Value
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

    def render(self):
        '''
        Return a render of the underlying Item in this Value
        '''
        return self.item.render()

    def render_all(self):
        return self.render()

    def repr_all(self):
        return repr(self)

    def set_copy_on_change(self):
        self.copy_on_change = True

    def unresolved_paths(self, path):
        if self.item.unresolved:
            return { path }
        else:
            return set()
