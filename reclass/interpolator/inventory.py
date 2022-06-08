from collections import namedtuple, OrderedDict
from ..node.node import Node
from ..value.hierarchy import Hierarchy

InventoryResult = namedtuple('InventoryResult', [ 'environment', 'exports' ])
CachedMerge = namedtuple('CachedMerge', [ 'exports', 'parameters' ])

class Inventory:
    def __init__(self, resolver):
        self.resolver = resolver
        self.merge_cache = {}

    def _cached_merge(self, node):
        exports_merged = Hierarchy.merge_multiple([ klass.exports for klass in node.klasses ], 'exports')
        exports_merged.freeze()
        parameters_merged = Hierarchy.merge_multiple([ klass.parameters for klass in node.klasses ], 'parameters')
        parameters_merged.freeze()
        return CachedMerge(exports_merged, parameters_merged)

    def result(self, queries, environment, node_loader, klass_loader):
        if not queries:
            return {}
        self.merge_cache = {}
        proto_nodes = self.proto_nodes(queries, environment, node_loader)
        inventory = { proto.name: self.node_inventory(proto, klass_loader)
                      for proto in proto_nodes.values() if proto.exports_required }
        inventory = OrderedDict(sorted(inventory.items()))
        self.merge_cache = {}
        return inventory

    def proto_nodes(self, queries, environment, node_loader):
        proto_nodes = { proto.name: proto for proto in node_loader.nodes() }
        for proto in proto_nodes.values():
            proto.exports_required = set()
            for query in queries:
                if query.all_envs or proto.environment == environment:
                    proto.exports_required.update(query.exports)
        return proto_nodes

    def node_inventory(self, proto, klass_loader):
        node = Node(proto, klass_loader)
        classes = '\n'.join(node.classes)
        if classes not in self.merge_cache:
            self.merge_cache[classes] = self._cached_merge(node)
        exports_merged = Hierarchy.merge_multiple([ self.merge_cache[classes].exports, node.nodeklass.parameters, node.autoklass.parameters ], 'exports')
        parameters_merged = Hierarchy.merge_multiple([ self.merge_cache[classes].parameters, node.nodeklass.parameters, node.autoklass.parameters ], 'parameters')
        exports_resolved = self.resolver.resolve(exports_merged, parameters_merged, proto.exports_required)
        paths_present = { path for path in proto.exports_required if path in exports_resolved }
        exports_pruned = exports_resolved.extract(paths_present)
        return InventoryResult(proto.environment, exports_pruned)

    def parameters_required(self, proto, exports):
        required = set()
        for path in proto.exports_required:
            if path in exports:
                required |= set(exports[path].references)
        return required
