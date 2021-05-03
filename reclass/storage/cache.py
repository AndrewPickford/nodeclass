from reclass.node.klass import Klass
from reclass.node.protonode import ProtoNode

class KlassCache:
    def __init__(self, loader):
        self._loader = loader
        self._cache = {}

    def __getitem__(self, name):
        if name not in self._cache:
            self._cache[name] = Klass(name, *self._loader[name])
        return self._cache[name]


class NodeCache:
    def __init__(self, loader):
        self._loader = loader
        self._cache = {}

    def __getitem__(self, name):
        if name not in self._cache:
            data, url = self._loader[name]
            klass = Klass(name, data, url)
            environment = data.get('environment', None)
            self._cache[name] = ProtoNode(name, environment, klass)
        return self._cache[name]

    def nodes(self):
        for nodename in self._loader.nodes:
            yield self[nodename]
