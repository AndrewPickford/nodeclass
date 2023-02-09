import copy
from ..context import CONTEXT
from ..utils.url import PseudoUrl
from .exceptions import RecursiveClassInclude
from .klass import Klass, KlassID

class Node:
    ''' A nodeclass node
    '''

    def __init__(self, proto, klass_loader):
        '''
        proto: ProtoNode object
        klass_loader: dict like object of available classes, indexed by KlassID (namedtuple of class name, environment)
        '''
        self.name = proto.name
        self.environment = proto.environment
        self.inv_query_env = proto.inv_query_env
        self.autoklass = self._make_auto_class_dict()
        self.nodeklass = proto.klass
        self.klasses = []
        self.applications = []
        self.classes = []
        self.load_classes(self.nodeklass, self.name, klass_loader, classes_processed=set(), classes_processing=set(), applications_found=set(), is_node_klass=True)
        self.all_klasses = copy.copy(self.klasses)
        self.all_klasses.extend([self.nodeklass, self.autoklass])
        self.all_classes = copy.copy(self.classes)
        self.all_classes.append(self.name)
        return

    def __repr__(self):
        return '{0}(name={1}, applications={2}, classes={3}, klass={4})'.format(self.__class__.__name__,
            repr(self.name), repr(self.applications), repr(self.classes), repr(self.nodeklass))

    def __str__(self):
        return '(name={0}, applications={1}, classes={2}, klass={3})'.format(str(self.name),
            str(self.applications), str(self.classes), str(self.nodeklass))

    def _make_auto_class_dict(self):
        name = '__auto__'
        url = PseudoUrl(name, name)
        if not CONTEXT.settings.automatic_parameters:
            return Klass.from_class_dict(name, {}, url)
        auto_klass_dict = {
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
        return Klass.from_class_dict('__auto__', auto_klass_dict, '__auto__')

    def load_classes(self, klass, classname, klass_loader, classes_processed, classes_processing, applications_found, is_node_klass=False):
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

    def to_dict(self):
        dictionary = {
            'applications': self.applications,
            'classes': self.classes,
            'environment': self.environment,
        }
        return dictionary
