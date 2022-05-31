from ..value.hierarchy import Hierarchy
from .exports_resolver import ExportsResolver
from .interpolatednode import InterpolatedNode
from .inventory import Inventory
from .inventory_resolver import InventoryResolver
from .parameters_resolver import ParametersResolver


class Interpolator:
    '''
    '''

    def __init__(self):
        self.exports_resolver = ExportsResolver()
        self.parameters_resolver = ParametersResolver()
        self.inventory_resolver = InventoryResolver(self.parameters_resolver)
        self.inventory = Inventory(self.inventory_resolver)

    def interpolate(self, node, node_loader, klass_loader):
        exports_merged = Hierarchy.merge_multiple([ klass.exports for klass in node.all_klasses ])
        parameters_merged = Hierarchy.merge_multiple([ klass.parameters for klass in node.all_klasses ])
        inventory_queries = parameters_merged.inventory_queries()
        inventory_resolved = self.inventory.resolve(inventory_queries, node.environment, node_loader, klass_loader)
        parameters_resolved = self.parameters_resolver.resolve(node.environment, parameters_merged, inventory_resolved)
        exports_resolved = self.exports_resolver.resolve(exports_merged, parameters_resolved)
        return InterpolatedNode(node.applications, node.classes, node.environment, exports_resolved.render_all(), parameters_resolved.render_all())