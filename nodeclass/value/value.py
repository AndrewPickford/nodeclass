from abc import ABC, abstractmethod

class Value(ABC):
    '''
    '''

    PLAIN = 0
    DICTIONARY = 1
    LIST = 2
    MERGED = 3
    HIERARCHY = 4

    __slots__ = ('copy_on_change', 'url')

    def __init__(self, url, copy_on_change):
        self.url = url
        self.copy_on_change = copy_on_change

    @property
    def references(self):
        '''
        Return a set of the references needed by this Value alone, excluding
        any references required by contained values.
        '''
        return set()

    @property
    def unresolved(self):
        '''
        Returns True if the Value requires any references, else returns False
        '''
        return False

    def inventory_queries(self):
        '''
        Return a set of all the inventory queries in this Value and any contained Values.
        '''
        return set()

    def unresolved_paths(self, path):
        '''
        Return a set of all the paths in this Value and any contained Values
        that have references.

        path: Path prefix
        '''
        return set()

    @abstractmethod
    def set_copy_on_change(self):
        '''
        Set the copy on change flag on this Value and any Values this value contains.
        Changes to this value will then copy the value, change the copy and return
        the changed copy.
        '''

    @abstractmethod
    def description(self) -> 'str':
        pass

    @abstractmethod
    def merge(self, other):
        '''
        Merge a Value onto another Value in preparation for interpolation.
        Potentially changes the current object, this depends on the type of
        objects being merged.
        May return self or a different Value object.

        Usage:

        foo = foo.merge(bar)

        It is not allowed to merge an already merged Value onto another Value,
        for example:

        a = value.Create(dictA)
        b = value.Create(dictB)
        c = value.Create(dictC)
        d = value.Create(dictD)
        e = value.Create(dictE)

        a = a.merge(b)   #  allowed, unmerged Dictionaries b and c are merged
        a = a.merge(c)   #  onto a in turn

        d = d.merge(e)   #  allowed
        a = a.merge(d)   #  not allowed, d has already been merged with e

        other: value to merge in
        returns: merged Value object
        '''
        pass
