from .value import Value


class Merged(Value):
    '''
    Wrap two Dictionary, List or Plain Value objects for later evaluation
    during the interpolation step.

    Use the merge method to add additional Value objects to an existing
    Merged object.
    '''
    type = Value.MERGE

    def __init__(self, first, second):
        super().__init__([ first.uri, second.uri ], False)
        self._values = [ first, second ]

    def __repr__(self):
        return '{0}[{1}]'.format(self.__class__.__name__, ','.join(map(repr, self._values)))

    def __str__(self):
        return '[{0}]'.format(','.join(map(str, self._values)))

    def unresolved(self):
        '''
        Merged Values are only created if at least one of the Values to
        be merged is unresolved
        '''
        return True

    def unresolved_paths(self, path):
        '''
        Merged Values always have at least one contained Item with references
        '''
        return { path }

    def references(self):
        refs = []
        for v in self._values:
            refs.extend(v.references())
        return refs

    def merge(self, other):
        if other.type == Value.MERGE:
            self._values.extend(other._values)
        else:
            self._values.append(other)
        if other.complex:
            self.complex = True
        return self
