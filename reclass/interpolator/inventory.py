from collections import namedtuple
from reclass.node.node import Node

InventoryResult = namedtuple('InventoryResult', [ 'environment', 'exports' ])

class Inventory:
    def __init__(self, merger, resolver):
        self.merger = merger
        self.resolver = resolver
        self.merge_cache = {}

    def resolve(self, queries, environment, nodes_loader, klasses_loader):
        self.merge_cache = {}
        proto_nodes = self.proto_nodes(queries, environment, nodes_loader)
        inventory = { proto.name: self.node_inventory(proto, klasses_loader)
                      for proto in proto_nodes.values() if proto.exports_required }
        self.merge_cache = {}
        return inventory

    def proto_nodes(self, queries, environment, nodes_loader):
        proto_nodes = { proto.name: proto for proto in nodes_loader.nodes() }
        for proto in proto_nodes.values():
            proto.exports_required = set()
            for query in queries:
                if query.all_envs or proto.environment == environment:
                    proto.exports_required.update(query.exports)
        return proto_nodes

    def node_inventory(self, proto, klasses_loader):
        node = Node(proto.name, proto.environment, proto.klass, klasses_loader)
        classes = '\n'.join(node.classes)
        exports_merged = self.merger.merge_exports(node.klasses)
        if classes not in self.merge_cache:
            self.merge_cache[classes] = self.merger.merge_parameters(node.klasses)
        parameters_merged = self.merger.merge_over_parameters(self.merge_cache[classes], [ node.nodeklass, node.baseklass ])
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
