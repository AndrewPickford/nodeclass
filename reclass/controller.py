import copy
from .interpolator.interpolator import Interpolator
from .invquery.parser import Parser as InvQueryParser
from .item.composite import Composite
from .item.invquery import InvQuery
from .item.parser import Parser as ItemParser
from .item.reference import Reference
from .item.scalar import Scalar
from .invquery.operator import OpTest
from .invquery.operand import Operand
from .invquery.iftest import IfTest
from .invquery.query import IfQuery, ListIfQuery, ValueQuery
from .storage.factory import Factory as StorageFactory
from .utils.path import Path
from .value.dictionary import Dictionary
from .value.factory import ValueFactory
from .value.list import List
from .value.merged import Merged
from .value.plain import Plain
from .value.topdictionary import TopDictionary


class Controller:
    def __init__(self, settings):
        self.settings = copy.copy(settings)
        self.xclasses()
        self.item_parser = self.ItemParser(self.settings)
        self.value_factory = self.ValueFactory(self.settings, self.item_parser)
        self.storage_factory = StorageFactory(self.value_factory)
        self.interpolator = Interpolator()

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
        self.TopDictionary = type('XTopDictionary', (TopDictionary, ), { 'Dictionary': self.Dictionary, 'Path': self.Path })
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
