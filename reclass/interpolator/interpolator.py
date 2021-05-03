import copy
from collections import namedtuple
from reclass.invquery.parser import Parser as InvQueryParser
from reclass.item.composite import Composite
from reclass.item.invquery import InvQuery
from reclass.item.parser import Parser as ItemParser
from reclass.item.reference import Reference
from reclass.item.scalar import Scalar
from reclass.invquery.operator import OpTest
from reclass.invquery.operand import Operand
from reclass.invquery.iftest import IfTest
from reclass.invquery.query import IfQuery, ListIfQuery, ValueQuery
from reclass.value.dictionary import Dictionary
from reclass.value.factory import ValueFactory
from reclass.value.list import List
from reclass.value.merged import Merged
from reclass.value.plain import Plain
from reclass.value.topdictionary import TopDictionary
from reclass.utils.path import Path
from .exports_resolver import ExportsResolver
from .inventory import Inventory
from .inventory_resolver import InventoryResolver
from .merger import Merger
from .parameters_resolver import ParametersResolver

InterpolatedNode = namedtuple('InterpolatedNode', ['applications', 'classes', 'environment', 'exports', 'parameters'])


class Interpolator:
    '''
    '''

    def __init__(self, settings):
        self.settings = copy.copy(settings)
        self.xclasses()
        self.item_parser = self.ItemParser(self.settings)
        self.value_factory = self.ValueFactory(self.settings, self.item_parser)
        self.merger = self.Merger(self.value_factory)
        self.exports_resolver = self.ExportsResolver()
        self.parameters_resolver = self.ParametersResolver()
        self.inventory_resolver = self.InventoryResolver(self.parameters_resolver)
        self.inventory = self.Inventory(self.merger, self.inventory_resolver)

    def xclasses(self):
        self.Path = type('XPath', (Path, ), {'delimiter': self.settings.delimiter})
        self.Scalar = type('XScalar', (Scalar, ), {})
        self.Reference = type('XReference', (Reference, ), { 'Path': self.Path, 'settings': self.settings })
        self.Composite = type('XComposite', (Composite, ), { 'Scalar': self.Scalar, 'settings': self.settings })
        self.InvQuery = type('XInvQuery', (InvQuery, ), { 'settings': self.settings })
        self.Merged = type('XMerged', (Merged, ), { 'settings': self.settings })
        self.Plain = type('XPlain', (Plain, ), { 'settings': self.settings, 'Merged': self.Merged })
        self.Dictionary = type('XDictionary', (Dictionary, ), { 'settings': self.settings, 'Merged': self.Merged })
        self.List = type('XList', (List, ), { 'settings': self.settings, 'Merged': self.Merged })
        self.TopDictionary = type('XTopDictionary', (TopDictionary, ), { 'Dictionary': self.Dictionary })
        self.OpTest = type('XOpTest', (OpTest, ), {})
        self.Operand = type('XOperand', (Operand, ), { 'Path': self.Path })
        self.IfTest = type('XIfTest', (IfTest, ), { 'Operand': self.Operand, 'OpTest': self.OpTest })
        self.IfQuery = type('XIfQuery', (IfQuery, ), { 'IfTest': self.IfTest, 'Dictionary': self.Dictionary, 'Operand': self.Operand })
        self.ListIfQuery = type('XListIfQuery', (ListIfQuery, ), { 'IfTest': self.IfTest, 'List': self.List })
        self.ValueQuery = type('XValueQuery', (ValueQuery, ), { 'Dictionary': self.Dictionary, 'Operand': self.Operand })
        self.InvQueryParser = type(
            'XInvQueryParser', (InvQueryParser, ),
            { 'IfQuery': self.IfQuery, 'ListIfQuery': self.ListIfQuery, 'ValueQuery': self.ValueQuery })
        self.ItemParser = type(
            'XItemParser', (ItemParser, ),
            { 'Composite': self.Composite, 'InvQuery': self.InvQuery, 'Reference': self.Reference,
              'Scalar': self.Scalar, 'InvQueryParser': self.InvQueryParser })
        self.ValueFactory = type(
            'XValueFactory', (ValueFactory, ),
            { 'Dictionary': self.Dictionary, 'List': self.List, 'Merged': self.Merged, 'Plain': self.Plain,
              'Scalar': self.Scalar, 'TopDictionary': self.TopDictionary })
        self.Merger = type('XMerger', (Merger, ), {})
        self.ExportsResolver = type('XExportsResolver', (ExportsResolver, ), { 'Path': self.Path })
        self.InventoryResolver = type('XInventoryResolver', (InventoryResolver, ), { 'Path': self.Path })
        self.ParametersResolver = type('XParametersResolver', (ParametersResolver, ), { 'Path': self.Path })
        self.Inventory = type('XInventory', (Inventory, ), {})


    def interpolate(self, node, nodes_loader, klasses_loader):
        parameters_merged = self.merger.merge_parameters(node.all_klasses)
        exports_merged = self.merger.merge_exports(node.all_klasses)
        inventory_queries = parameters_merged.inventory_queries()
        inventory_resolved = self.inventory.resolve(inventory_queries, node.environment, nodes_loader, klasses_loader)
        parameters_resolved = self.parameters_resolver.resolve(node.environment, parameters_merged, inventory_resolved)
        exports_resolved = self.exports_resolver.resolve(exports_merged, parameters_resolved)
        return InterpolatedNode(node.applications, node.classes, node.environment, exports_resolved, parameters_resolved)
