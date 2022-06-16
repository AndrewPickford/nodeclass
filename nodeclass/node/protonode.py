class ProtoNode:
    ''' A light weight description of a node from only the node klass file

        Used by the inventory resolver to determine if the full node needs
        to be loaded.
    '''

    def __init__(self, name, environment, klass, url):
        self.name = name
        self.environment = environment
        self.klass = klass
        self.url = url

    def __repr__(self):
        return '{0}(name={1}, environment={2}, klass={3}; url={4})'.format(self.__class__.__name__,
                   repr(self.name), repr(self.environment), repr(self.klass), repr(self.url))

    def __str__(self):
        return '(name={0}, environment={1}, klass={2}; url={3})'.format(str(self.name),
                   str(self.environment), str(self.klass), str(self.url))
