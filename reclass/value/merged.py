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

    def __init__(self, first, second):
        super().__init__([ first.url, second.url ])
        self._values = [ first, second ]

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

    def unresolved_paths(self, path):
        '''
        Merged Values always have at least one contained Item with references
        '''
        return { path }

    def merge(self, other):
        '''
        Merged objects merge new objects on top by appending to the list of
        values to merge.
        Merging two Merged objects should never happen.
        '''
        if other.type == Value.MERGED:
            raise MergeTypeError(self, other)
        self._values.append(other)
        return self

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
            val = copy.copy(self._values[0])
            for v in self._values[1:]:
                val = val.merge(v)
            return val, True
