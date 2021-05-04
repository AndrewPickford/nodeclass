from reclass.node.klass import Klass
from reclass.node.protoklass import ProtoKlass
from reclass.node.protonode import ProtoNode


def make_klass(name, class_dict, url, value_factory):
    proto = ProtoKlass(name, class_dict, url)
    parameters = value_factory.make_value_dictionary(proto.parameters, proto.url)
    exports = value_factory.make_value_dictionary(proto.exports, proto.url)
    parameters.freeze()
    exports.freeze()
    return Klass(proto, parameters, exports), proto.environment


class KlassLoader:
    def __init__(self, storage, value_factory):
        self.storage = storage
        self.value_factory = value_factory
        self.cache = {}

    def __getitem__(self, name):
        if name not in self.cache:
            class_dict, url = self.storage[name]
            klass, _ = make_klass(name, class_dict, url, self.value_factory)
            self.cache[name] = klass
        return self.cache[name]

    def generated_klass(self, name, applications, classes, exports, parameters, url):
        class_dict = { 'applications': applications, 'classes': classes,
                      'exports': exports, 'parameters': parameters }
        klass, _ = make_klass(name, class_dict, url, self.value_factory)
        return klass

class NodeLoader:
    def __init__(self, storage, value_factory):
        self.storage = storage
        self.value_factory = value_factory
        self.cache = {}

    def __getitem__(self, name):
        if name not in self.cache:
            class_dict, url = self.storage[name]
            klass, environment = make_klass(name, class_dict, url, self.value_factory)
            self.cache[name] = ProtoNode(name, environment, klass)
        return self.cache[name]

    def nodes(self):
        for nodename in self.storage.nodes:
            yield self[nodename]
