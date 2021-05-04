from copy import copy
from .klass import Klass

class Node:
    ''' A reclass node
    '''

    def __init__(self, proto, klass_loader):
        '''
        proto: ProtoNode object
        klass_loader: dict like object of available classes, indexed by class name
        '''
        self.name = proto.name
        self.environment = proto.environment
        self.nodeklass = proto.klass
        self.baseklass = klass_loader.generated_klass('__base__', [], [], {}, self.base_parameters(), '__base__')
        self.klasses = []
        self.applications = []
        self.classes = []
        self.load_classes(self.nodeklass, self.name, klass_loader, classes_found=set(), applications_found=set(), append=False)
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

    def base_parameters(self):
        params = {
            '_reclass_': {
                'environment': self.environment,
                'name': {
                    'full': self.name,
                    'short': self.name.split('.')[0]
                },
            }
        }
        return params

    def load_classes(self, klass, classname, klass_loader, classes_found, applications_found, append=True):
        '''
        '''
        classes_found.add(classname)
        for application in klass.applications:
            if application not in applications_found:
                applications_found.add(application)
                self.applications.append(application)
        for name in klass.classes:
            if name not in classes_found:
                self.load_classes(klass_loader[name], name, klass_loader, classes_found, applications_found)
        if append:
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
