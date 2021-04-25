from reclass.item import Scalar
from .exceptions import MergeTypeError
from .merged import Merged
from .value import Value


class Plain(Value):
    '''
    '''
    type = Value.PLAIN

    def __init__(self, input, uri, parse_func):
        super().__init__(uri)
        if isinstance(input, str):
            self.item = parse_func(input)
        else:
            self.item = Scalar(input)

    def __copy__(self):
        '''
        No need to actually copy as whatever final value this renders to any 'copy' will need to
        render to the same thing.
        '''
        return self

    def __repr__(self):
        return '{0}({1}; {2})'.format(self.__class__.__name__, repr(self.item), repr(self.uri))

    def __str__(self):
        return '({0}; {1})'.format(str(self.item), str(self.uri))

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

    def merge(self, other, settings):
        if other.type == Value.PLAIN:
            # if both Plain objects have no references just handle the merge
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
            else:
                raise MergeTypeError(self, other)
        else:
            raise MergeTypeError(self, other)

    def resolve(self, context, inventory, settings):
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
        settings: control settings
        returns: tuple of resolved Value and a bool which is true if new unresolved paths
                 could be present in the return Value
        '''
        value = self.item.resolve_to_value(context, inventory, settings)
        if value is None:
            self.item = self.item.resolve_to_item(context, inventory, settings)
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
