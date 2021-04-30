import copy
from collections import namedtuple
from reclass.invquery.parser import Parser as InvQueryParser
from reclass.item.parser import Parser as ItemParser
from reclass.value.factory import ValueFactory
from reclass.utils.path import Path
from .full_resolver import FullResolver
#from .inventorymanager import InventoryManager
from .merger import Merger

InterpolatedNode = namedtuple('InterpolatedNode', ['applications', 'classes', 'environment', 'exports', 'parameters'])

class Interpolator:
    '''
    '''

    def __init__(self, settings):
        self.settings = copy.copy(settings)
        self.Path = type('XPath', (Path, ), {'delimiter': settings.delimiter})
        self.invquery_parser = InvQueryParser(self.Path)
        self.item_parser = ItemParser(self.settings, self.Path, self.invquery_parser)
        self.value_factory = ValueFactory(self.settings, self.item_parser)
        self.merger = Merger(self.value_factory)
        #self.inventory_manager = InventoryManager(nodes_loader, klasses_loader)
        self.full_resolver = FullResolver(self.Path)

    def interpolate(self, node, nodes_loader, klasses_loader):
        parameters = self.merger.merge_parameters(node.klasses)
        exports = self.merger.merge_exports(node.klasses)
        queries = parameters.inventory_queries()
        #inventory = inventory_manager.create(queries, parameters, exports)
        inventory = {}
        exports_resolved = self.full_resolver.resolve(exports)
        parameters_resolved = self.full_resolver.resolve(parameters, inventory)
        return InterpolatedNode(node.applications, node.classes, node.environment,
                                exports_resolved, parameters.resolved)
