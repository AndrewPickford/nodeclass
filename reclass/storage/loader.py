from ..node.klass import Klass
from ..node.protonode import ProtoNode
from .exceptions import FileError


class KlassLoader:
    def __init__(self, storage):
        self.storage = storage
        self.cache = {}

    def __getitem__(self, klass_id):
        ''' Load/Get a class

            klass_id: KlassID namedtuple
        '''
        try:
            name, environment = klass_id
            if klass_id not in self.cache:
                class_dict, url = self.storage.get(name, environment)
                self.cache[klass_id] = Klass.from_class_dict(name, class_dict, url)
            return self.cache[klass_id]
        except FileError as exception:
            exception.environment = environment
            exception.storage = self.storage
            raise

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.storage)

    def __str__(self):
        return '{0}'.format(self.storage)


class NodeLoader:
    def __init__(self, storage):
        self.storage = storage
        self.cache = {}

    def __getitem__(self, name):
        if name not in self.cache:
            class_dict, url = self.storage.get(name)
            environment = class_dict.get('environment', None)
            klass = Klass.from_class_dict(name, class_dict, url)
            self.cache[name] = ProtoNode(name, environment, klass, url)
        return self.cache[name]

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.storage)

    def __str__(self):
        return '{0}'.format(self.storage)

    def nodes(self):
        for nodename in self.storage.node_map:
            yield self[nodename]
