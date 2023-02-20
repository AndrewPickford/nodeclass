from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..utils.url import Url
    from .klass import Klass

class ProtoNode:
    ''' A light weight description of a node from only the node klass file

        Used by the inventory resolver to determine if the full node needs
        to be loaded.
    '''

    def __init__(self, name: 'str', environment: 'str', klass: 'Klass', url: 'Url'):
        self.name = name
        self.environment = environment
        self.inv_query_env = environment
        self.klass = klass
        self.url = url

    def __repr__(self) -> 'str':
        return '{0}(name={1}, environment={2}, klass={3}; url={4})'.format(self.__class__.__name__,
                   repr(self.name), repr(self.environment), repr(self.klass), repr(self.url))

    def __str__(self) -> 'str':
        return '(name={0}, environment={1}, klass={2}; url={3})'.format(str(self.name),
                   str(self.environment), str(self.klass), str(self.url))
