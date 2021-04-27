from .exceptions import MergeTypeError
from .merged import Merged as BaseMerged
from .value import Value


class Plain(Value):
    '''
    '''
    type = Value.PLAIN
    Merged = BaseMerged

    def __init__(self, item, url):
        super().__init__(url)
        self.item = item

    def __copy__(self):
        '''
        No need to actually copy as whatever final value this renders to any 'copy' will need to
        render to the same thing.
        '''
        return self

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self.item), repr(self.url))

    def __str__(self):
        return '({0}; {1})'.format(str(self.item), str(self.url))

    def _unresolved_ancestor(self, path, depth):
        if depth <= path.last and self.item.unresolved:
            return True
        raise KeyError('{0} not present'.format(str(path)))

    @property
    def unresolved(self):
        return self.item.unresolved

    @property
    def references(self):
        return self.item.references

    def unresolved_paths(self, path):
        if self.item.unresolved:
            return { path }
        else:
            return set()

    def merge(self, other):
        if other.type == Value.PLAIN:
            # if both Plain objects have no references just handle the merge
            # by returning the other object, otherwise return a Merged object
            # for later interpolation
            if self.unresolved or other.unresolved:
                return self.Merged(self, other)
            else:
                return other
        elif other.type == Value.DICTIONARY or other.type == Value.LIST:
            # if the current object is unresolved return a Merged object for later
            # interpolation, otherwise raise an error
            if self.unresolved:
                return self.Merged(self, other)
            elif self.item.contents is None and self.settings.allow_none_overwrite:
                return other
        raise MergeTypeError(self, other)

    def resolve(self, context, inventory):
        '''
        Step through one level of indirection.

        Check if the Item we have is a simple reference, ${foo}, which can be
        resolved as the Value in the context dictionary the reference is pointing
        to. If this is the case return the referenced Value.
        If not use resolve_to_item to return a new item which has removed a level
        of indirection. Set self.item to this Item and return self as the resolved
        Value.

        context: Dictionary of resolved parameter values
        inventory: Dictionary of required inventory query answers
        returns: tuple of resolved Value and a bool which is true if new unresolved paths
                 could be present in the return Value
        '''
        value = self.item.resolve_to_value(context, inventory)
        if value is None:
            self.item = self.item.resolve_to_item(context, inventory)
            return self, True
        else:
            return value, False

    def render(self):
        '''
        Return a render of the underlying Item in this Value
        '''
        return self.item.render()

    def render_all(self):
        return self.render()
