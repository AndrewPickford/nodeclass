import copy
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
        super().__init__([ first.uri, second.uri ])
        self._values = [ first, second ]

    def __repr__(self):
        return '{0}[{1}]'.format(self.__class__.__name__, ','.join(map(repr, self._values)))

    def __str__(self):
        return '[{0}]'.format(','.join(map(str, self._values)))

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
        It is not allowed to merge to Merged objected together.
        '''
        if other.type == Value.MERGED:
            raise MergeTypeError(self, other)
        self._values.append(other)
        return self

    def resolve(self, context, inventory):
        '''
        '''
        unresolved = False
        for i, v in enumerate(self._values):
            if v.unresolved:
                self._values[i], unres = v.resolve(context, inventory)
                if unres:
                    unresolved = True
        if unresolved:
            return self, False
        else:
            val = copy.copy(self._values[0])
            for v in self._values[1:]:
                val = val.merge(v)
            return val, True
