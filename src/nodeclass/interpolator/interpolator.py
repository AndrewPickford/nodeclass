from ..exceptions import ProcessError
from ..value.hierarchy import Hierarchy
from .exceptions import InventoryError, InventoryQueryError
from .exports_resolver import ExportsResolver
from .interpolatednode import InterpolatedNode
from .inventory import Inventory
from .inventory_resolver import InventoryResolver
from .parameter_analyser import ParameterAnalyser
from .parameters_resolver import ParametersResolver


class Interpolator:
    '''
    '''

    def __init__(self):
        self.exports_resolver = ExportsResolver()
        self.parameters_resolver = ParametersResolver()
        self.inventory_resolver = InventoryResolver(self.parameters_resolver)
        self.inventory = Inventory(self.inventory_resolver)

    def parameter_analysis(self, parameter, node, node_loader, klass_loader):
        analyser = ParameterAnalyser(parameter)
        self._interpolate_node(node, node_loader, klass_loader, analyser)
        return analyser

    def interpolate(self, node, node_loader, klass_loader):
        return self._interpolate_node(node, node_loader, klass_loader, None)

    def _interpolate_node(self, node, node_loader, klass_loader, analyser):
        exports_merged = Hierarchy.merge_multiple([ klass.exports for klass in node.all_klasses ], 'exports')
        parameters_merged = Hierarchy.merge_multiple([ klass.parameters for klass in node.all_klasses ], 'parameters', analyser=analyser)
        inventory_queries = parameters_merged.inventory_queries()
        try:
            inventory_result = self.inventory.result(inventory_queries, node.inv_query_env, node_loader, klass_loader)
        except InventoryQueryError as exception:
            try:
                exception.path = parameters_merged.find_matching_contents_path(exception.query)
                exception.category = parameters_merged.category
                exception.url = parameters_merged[exception.path].url
            except Exception:
                pass
            raise
        except ProcessError as exception:
            raise InventoryError(exception)
        parameters_resolved = self.parameters_resolver.resolve(node.inv_query_env, parameters_merged, inventory_result)
        exports_resolved = self.exports_resolver.resolve(exports_merged, parameters_resolved)
        return InterpolatedNode(node.name, node.applications, node.classes, node.environment, exports_resolved.render_all(), parameters_resolved.render_all())
