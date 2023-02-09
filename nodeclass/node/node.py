import copy
from ..context import CONTEXT
from ..utils.url import PseudoUrl
from .exceptions import RecursiveClassInclude
from .klass import Klass, KlassID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, List, Set
    from ..storage.loader import KlassLoader
    from .protonode import ProtoNode

class Node:
    ''' A nodeclass node
    '''

    def __init__(self, proto: 'ProtoNode', klass_loader: 'KlassLoader'):
        '''
        proto: ProtoNode object
        klass_loader: dict like object of available classes, indexed by KlassID (namedtuple of class name, environment)
        '''
        self.name = proto.name
        self.environment = proto.environment
        self.inv_query_env = proto.inv_query_env
        self.autoklass = self._make_auto_class_dict()
        self.nodeklass = proto.klass
        self.klasses: 'List[Klass]' = []
        self.applications: 'List[str]' = []
        self.classes: 'List[str]' = []
        self.load_classes(self.nodeklass, self.name, klass_loader, classes_processed=set(), classes_processing=set(), applications_found=set(), is_node_klass=True)
        self.all_klasses = copy.copy(self.klasses)
        self.all_klasses.extend([self.nodeklass, self.autoklass])
        self.all_classes = copy.copy(self.classes)
        self.all_classes.append(self.name)
        return

    def __repr__(self) -> 'str':
        return '{0}(name={1}, applications={2}, classes={3}, klass={4})'.format(self.__class__.__name__,
            repr(self.name), repr(self.applications), repr(self.classes), repr(self.nodeklass))

    def __str__(self) -> 'str':
        return '(name={0}, applications={1}, classes={2}, klass={3})'.format(str(self.name),
            str(self.applications), str(self.classes), str(self.nodeklass))

    def _make_auto_class_dict(self) -> 'Klass':
        name = '__auto__'
        url = PseudoUrl(name, name)
        if not CONTEXT.settings.automatic_parameters:
            return Klass.from_class_dict(name, {}, url)
        auto_klass_dict: 'Dict' = {
            'applications': [],
            'classes': [],
            'exports': {},
            'parameters': {
                CONTEXT.settings.automatic_parameters_name: {
                    'environment': self.environment,
                    'name': {
                    'full': self.name,
                    'short': self.name.split('.')[0]
                    }
                }
            }
        }
        return Klass.from_class_dict(name, auto_klass_dict, url)

    def load_classes(self, klass: 'Klass', classname: 'str', klass_loader: 'KlassLoader', classes_processed: 'Set[str]',
                     classes_processing: 'Set[str]', applications_found: 'Set[str]', is_node_klass: 'bool' = False):
        '''
        '''
        if not is_node_klass:
            classes_processing.add(classname)
        for application in klass.applications:
            if application not in applications_found:
                applications_found.add(application)
                self.applications.append(application)
        for name in klass.classes:
            if name in classes_processing:
                raise RecursiveClassInclude(name, klass.url)
            if name not in classes_processed:
                try:
                    self.load_classes(klass_loader[KlassID(name, self.environment)], name, klass_loader, classes_processed, classes_processing, applications_found)
                except RecursiveClassInclude as exception:
                    if exception.second is None and name == exception.classname:
                        exception.second = klass.url
                    raise
        if not is_node_klass:
            self.classes.append(classname)
            self.klasses.append(klass)
            classes_processed.add(classname)
            classes_processing.remove(classname)
        return

    def to_dict(self) -> 'Dict':
        dictionary = {
            'applications': self.applications,
            'classes': self.classes,
            'environment': self.environment,
        }
        return dictionary
