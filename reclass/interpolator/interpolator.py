import copy
from .exports_resolver import ExportsResolver
from .interpolatednode import InterpolatedNode
from .inventory import Inventory
from .inventory_resolver import InventoryResolver
from .merger import Merger
from .parameters_resolver import ParametersResolver


class Interpolator:
    '''
    '''

    def __init__(self):
        self.merger = Merger()
        self.exports_resolver = ExportsResolver()
        self.parameters_resolver = ParametersResolver()
        self.inventory_resolver = InventoryResolver(self.parameters_resolver)
        self.inventory = Inventory(self.merger, self.inventory_resolver)

    def interpolate(self, node, node_loader, klass_loader):
        parameters_merged = self.merger.merge_parameters(node.all_klasses)
        exports_merged = self.merger.merge_exports(node.all_klasses)
        inventory_queries = parameters_merged.inventory_queries()
        inventory_resolved = self.inventory.resolve(inventory_queries, node.environment, node_loader, klass_loader)
        parameters_resolved = self.parameters_resolver.resolve(node.environment, parameters_merged, inventory_resolved)
        exports_resolved = self.exports_resolver.resolve(exports_merged, parameters_resolved)
        return InterpolatedNode(node.applications, node.classes, node.environment, exports_resolved.render_all(), parameters_resolved.render_all())
