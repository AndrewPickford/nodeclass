import logging

from collections import OrderedDict
from typing import NamedTuple
from ..exceptions import ProcessError
from ..node.node import Node
from ..value.hierarchy import Hierarchy
from .exceptions import InventoryQueryError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict


log = logging.getLogger(__name__)


class InventoryResult(NamedTuple):
    environment: 'str'
    exports: 'Hierarchy'


class CachedMerge(NamedTuple):
    exports: 'Hierarchy'
    parameters: 'Hierarchy'


if TYPE_CHECKING:
    InventoryDict = Dict[str, InventoryResult]


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
        proto_nodes = self.proto_nodes(queries, environment, node_loader)
        inventory = {}
        for proto in proto_nodes.values():
            if proto.queries:
                try:
                    inventory[proto.name] = self.node_inventory(proto, klass_loader)
                except InventoryQueryError as exception:
                    if exception.query.ignore_errors:
                       log.warning('failed to get inventory for {0}'.format(proto.name))
                    else:
                        exception.exception.node = proto.name
                        raise
                except ProcessError as exception:
                    exception.node = proto.name
                    raise
        inventory = OrderedDict(sorted(inventory.items()))
        return inventory

    def proto_nodes(self, queries, environment, node_loader):
        proto_nodes = { proto.name: proto for proto in node_loader.nodes() }
        for proto in proto_nodes.values():
            proto.queries = []
            proto.exports_required = set()
            for query in queries:
                if query.all_envs or proto.inv_query_env == environment:
                    proto.queries.append(query)
                    proto.exports_required.update(query.exports)
        return proto_nodes

    def node_inventory(self, proto, klass_loader):
        node = Node(proto, klass_loader)
        classes = '\n'.join(node.classes)
        klass_id = (node.environment, classes)
        if klass_id not in self.merge_cache:
            self.merge_cache[klass_id] = self._cached_merge(node)
        exports_merged = Hierarchy.merge_multiple([ self.merge_cache[klass_id].exports, node.nodeklass.exports, node.autoklass.exports ], 'exports')
        parameters_merged = Hierarchy.merge_multiple([ self.merge_cache[klass_id].parameters, node.nodeklass.parameters, node.autoklass.parameters ], 'parameters')
        exports_resolved = self.resolver.resolve(exports_merged, parameters_merged, proto.queries)
        paths_present = { path for path in proto.exports_required if path in exports_resolved }
        exports_pruned = exports_resolved.extract(paths_present)
        return InventoryResult(proto.inv_query_env, exports_pruned)

    #def parameters_required(self, proto, exports):
    #    required = set()
    #    for path in proto.exports_required:
    #        if path in exports:
    #            required |= set(exports[path].references)
    #    return required
