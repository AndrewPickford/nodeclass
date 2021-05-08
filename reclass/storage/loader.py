from ..node.klass import Klass
from ..node.protonode import ProtoNode
from ..value.make import make_value_dictionary


class KlassLoader:
    def __init__(self, storage):
        self.storage = storage
        self.cache = {}

    def __getitem__(self, name):
        if name not in self.cache:
            class_dict, url = self.storage[name]
            klass, _ = Klass.from_class_dict(name, class_dict, url)
            self.cache[name] = klass
        return self.cache[name]

    def generated_klass(self, name, applications, classes, exports, parameters, url):
        class_dict = { 'applications': applications, 'classes': classes,
                      'exports': exports, 'parameters': parameters }
        klass, _ = Klass.from_class_dict(name, class_dict, url)
        return klass

class NodeLoader:
    def __init__(self, storage):
        self.storage = storage
        self.cache = {}

    def __getitem__(self, name):
        if name not in self.cache:
            class_dict, url = self.storage[name]
            klass, environment = Klass.from_class_dict(name, class_dict, url)
            self.cache[name] = ProtoNode(name, environment, klass)
        return self.cache[name]

    def nodes(self):
        for nodename in self.storage.nodes:
            yield self[nodename]
