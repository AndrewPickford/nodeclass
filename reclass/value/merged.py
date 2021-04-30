import copy
from .exceptions import MergeTypeError
from .value import Value


class Merged(Value):
    '''
    Wrap two Dictionary, List or Plain Value objects for later evaluation
    during the interpolation step.

    Use the merge method to add additional Value objects to an existing
    Merged object.
    '''
    type = Value.MERGED

    def __init__(self, first, second, copy_on_change=False):
        super().__init__(url=[ first.url, second.url ], copy_on_change=copy_on_change)
        self._values = [ first, second ]

    def __copy__(self):
        c = type(self)(first=None, second=None, copy_on_change=False)
        c._values = copy.copy(self._values)
        c.url = [ c._values[0].url, c._values[1].url ]
        return c

    def __repr__(self):
        return '{0}[{1}]'.format(self.__class__.__name__, ','.join(map(repr, self._values)))

    def __str__(self):
        return '[{0}]'.format(','.join(map(str, self._values)))

    def _unresolved_ancestor(self, path, depth):
        if depth <= path.last:
            return True
        raise KeyError('{0} not present'.format(str(path)))

    @property
    def unresolved(self):
        '''
        Merged Values are only created if at least one of the Values to
        be merged is unresolved
        '''
        return True

    @property
    def references(self):
        refs = []
        for v in self._values:
            refs.extend(v.references)
        return refs

    def inventory_queries(self):
        queries = set()
        for v in self._values:
            queries.update(v.inventory_queries())
        return queries

    def unresolved_paths(self, path):
        '''
        Merged Values always have at least one contained Item with references
        '''
        return { path }

    def set_copy_on_change(self):
        self.copy_on_change = True
        for v in self._values:
            v.set_copy_on_change()

    def merge(self, other):
        '''
        Merged objects merge new objects on top by appending to the list of
        values to merge.
        Merging two Merged objects should never happen.
        '''
        if other.type == Value.MERGED:
            raise MergeTypeError(self, other)
        merged = copy.copy(self) if self.copy_on_change else self
        merged._values.append(other)
        return merged

    def resolve(self, context, inventory):
        '''
        '''
        potential_unresolved = False
        for i, v in enumerate(self._values):
            if v.unresolved:
                self._values[i], potential_unres = v.resolve(context, inventory)
                if potential_unres:
                    potential_unresolved = True
        if potential_unresolved:
            # there still may be unresolved references so return self and wait
            # until higher level logic calls our resolve method again.
            return self, True
        else:
            # everything is resolved so merge the values we have together and
            # return the new merged Value
            self.set_copy_on_change()
            val = self._values[0]
            for v in self._values[1:]:
                val = val.merge(v)
            return val, True
