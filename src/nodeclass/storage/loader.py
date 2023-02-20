from ..exceptions import InputError
from ..node.klass import Klass
from ..node.protonode import ProtoNode
from .exceptions import FileError, FileUnhandledError, InvalidNodeName

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..node.klass import KlassID

class KlassLoader:
    def __init__(self, storages):
        self.storages = storages
        self.cache = {}

    def __getitem__(self, klass_id: 'KlassID') -> 'Klass':
        ''' Load/Get a class

            klass_id: KlassID namedtuple
        '''
        name, environment = klass_id
        if klass_id not in self.cache:
            storage = self._match_storage(environment)
            try:
                class_dict, url = storage.get(name, environment)
                self.cache[klass_id] = Klass.from_class_dict(name, class_dict, url)
            except FileError as exception:
                exception.environment = environment
                exception.storage = str(storage)
                raise
            except InputError:
                raise
            except Exception as exception:
                raise FileUnhandledError(exception, environment=environment, storage=storage)
        return self.cache[klass_id]

    def __repr__(self) -> 'str':
        return '{0}({1})'.format(self.__class__.__name__, self.storages)

    def __str__(self) -> 'str':
        return '{0}'.format(self.storages)

    def _match_storage(self, environment):
        if environment is None or len(self.storages) == 1:
            return self.storages[-1][1]
        for env, storage in self.storages:
            if env == environment:
                return storage
        return self.storages[-1][1]


class NodeLoader:
    def __init__(self, storage):
        self.storage = storage
        self.cache = {}

    def __getitem__(self, name: 'str') -> 'ProtoNode':
        if name not in self.cache:
            try:
                # node names can not begin with a '.'
                if name[0] == '.':
                    raise InvalidNodeName(name, str(self.storage))
            except:
                raise InvalidNodeName(name, str(self.storage))
            class_dict, url = self.storage.get(name)
            environment = class_dict.get('environment', None)
            klass = Klass.from_class_dict(name, class_dict, url)
            self.cache[name] = ProtoNode(name, environment, klass, url)
        return self.cache[name]

    def __repr__(self) -> 'str':
        return '{0}({1})'.format(self.__class__.__name__, self.storage)

    def __str__(self) -> 'str':
        return '{0}'.format(self.storage)

    def nodes(self):
        for nodename in self.storage.node_map:
            yield self[nodename]

    def nodenames(self):
        for nodename in self.storage.node_map:
            yield nodename

    def primary(self, name: 'str', env_override: 'str') -> 'ProtoNode':
        node = self.__getitem__(name)
        if env_override:
            node.environment = env_override
        return node
