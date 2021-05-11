from ..node.klass import Klass
from ..node.protonode import ProtoNode


class KlassLoader:
    def __init__(self, storage):
        self.storage = storage
        self.cache = {}

    def __getitem__(self, name):
        if name not in self.cache:
            class_dict, url = self.storage[name]
            self.cache[name] = Klass.from_class_dict(name, class_dict, url)
        return self.cache[name]

class NodeLoader:
    def __init__(self, storage):
        self.storage = storage
        self.cache = {}

    def __getitem__(self, name):
        if name not in self.cache:
            class_dict, url = self.storage[name]
            environment = class_dict.get('environment', None)
            klass = Klass.from_class_dict(name, class_dict, url)
            self.cache[name] = ProtoNode(name, environment, klass)
        return self.cache[name]

    def nodes(self):
        for nodename in self.storage.nodes:
            yield self[nodename]
