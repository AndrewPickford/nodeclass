class Value:
    '''
    '''

    PLAIN = 0
    DICTIONARY = 1
    LIST = 2
    MERGE = 3

    def __init__(self, type, uri):
        self.type = type
        self.uri = uri

    def merge(self, other):
        '''
        Merge two Values in preparation for interpolation.
        Potentially changes the current object, this depends on the
        type of objects being merged.
        May return self or a different Value object.

        Usage:

        foo = foo.merge(bar)

        other: value to merge in
        returns: merged Value object
        '''
        raise MergeUndefinedError()

    def render(self):
        '''
        Return the underlying object in a Value, depending on the type of object:

        Dictionary: dict of rendered contents
        List: list of rendered contents
        Plain: the rendered Item

        Merged objects cannot be rendered.
        Plain objects containing references cannot be rendered.
        '''
        raise ValueRenderUndefinedError(self)
