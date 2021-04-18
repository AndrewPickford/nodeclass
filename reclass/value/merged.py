from .value import Value


class Merged(Value):
    '''
    '''

    def __init__(self, first, second):
        '''
        Wrap two Dictionary, List or Plain Value objects for
        later evaluation during the interpolation step.

        Use the merge method to add additional Value objects to an
        existing Merged object.
        '''
        super().__init__(Value.MERGE, [ first.uri, second.uri ])
        self.values = [ first, second ]

    def merge(self, other):
        if other.type == Value.MERGE:
            self.values.extend(other.values)
        else:
            self.values.append(other)
        return self

    def merge_under(self, other):
        if other.type == Value.MERGE:
            return merge(other)
        else:
            self.values.insert(0, other)
            return self

    def __str__(self):
        return '[{0}]'.format(','.join(map(str, self.values)))

    def __repr__(self):
        return '{0}[{1}]'.format(self.__class__.__name__, ','.join(map(repr, self.values)))
