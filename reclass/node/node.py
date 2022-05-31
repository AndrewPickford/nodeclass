from copy import copy
from .klass import Klass, KlassID

class Node:
    ''' A reclass node
    '''

    def __init__(self, proto, klass_loader):
        '''
        proto: ProtoNode object
        klass_loader: dict like object of available classes, indexed by KlassID (namedtuple of class name, environment)
        '''
        self.name = proto.name
        self.environment = proto.environment
        self.nodeklass = proto.klass
        self.baseklass = Klass.from_class_dict('__base__', self.base_class_dict(), '__base__')
        self.klasses = []
        self.applications = []
        self.classes = []
        self.load_classes(self.nodeklass, self.name, klass_loader, classes_found=set(), applications_found=set(), is_node_klass=True)
        self.all_klasses = copy(self.klasses)
        self.all_klasses.extend([self.nodeklass, self.baseklass])
        self.all_classes = copy(self.classes)
        self.all_classes.append(self.name)
        return

    def __repr__(self):
        return '{0}(name={1}, applications={2}, classes={3}, klass={4})'.format(self.__class__.__name__,
            repr(self.name), repr(self.applications), repr(self.classes), repr(self.nodeklass))

    def __str__(self):
        return '(name={0}, applications={1}, classes={2}, klass={3})'.format(str(self.name),
            str(self.applications), str(self.classes), str(self.nodeklass))

    def base_class_dict(self):
        return { 'applications': [],
                 'classes': [],
                 'exports': {},
                 'parameters': {
                     '_reclass_': {
                         'environment': self.environment,
                         'name': {
                             'full': self.name,
                             'short': self.name.split('.')[0] }}}}

    def load_classes(self, klass, classname, klass_loader, classes_found, applications_found, is_node_klass=False):
        '''
        '''
        classes_found.add(classname)
        for application in klass.applications:
            if application not in applications_found:
                applications_found.add(application)
                self.applications.append(application)
        for name in klass.classes:
            if name not in classes_found:
                self.load_classes(klass_loader[KlassID(name, self.environment)], name, klass_loader, classes_found, applications_found)
        if is_node_klass is False:
            self.classes.append(classname)
            self.klasses.append(klass)
        return

    def to_dict(self):
        dictionary = {
            'applications': self.applications,
            'classes': self.classes,
            'environment': self.environment,
            'exports': self.exports,
            'parameters': self.parameters
        }
        return dictionary