from .klass import Klass

class Node:
    ''' A reclass node
    '''

    def __init__(self, nodename, nodeklass, environment, klass_loader):
        '''
        nodename: full name of node
        nodeklass: base klass of the node
        environment: environment of the node
        klass_loader: dict like object of available classes, indexed by class name
        '''
        self.nodename = nodename
        self.nodeklass = nodeklass
        self.environment = environment
        self.klasses = [ Klass('_base_', { 'parameters': self.base_parameters() }, '_base_') ]
        self.applications = []
        self.classes = []
        self.load_classes(self.nodeklass, self.nodename, klass_loader, classes_found=set(), applications_found=set())

    def __repr__(self):
        return '{0}(nodeklass={1}, applications={2}, classes={3})'.format(
                   self.__class__.__name__, repr(self.applications), repr(self.classes))

    def __str__(self):
        return '(nodeklass={0}, applications={1}, classes={2})'.format(
                 str(self.nodeklass), str(self.applications), str(self.classes))

    def base_parameters(self):
        params = {
            '_reclass_': {
                'environment': self.environment,
                'name': {
                    'full': self.nodename,
                    'short': self.nodename.split('.')[0]
                },
            }
        }
        return params

    def load_classes(self, klass, classname, klass_loader, classes_found, applications_found):
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
        self.classes.append(classname)
        self.klasses.append(klass)

    def to_dict(self):
        dictionary = {
            'applications': self.applications,
            'classes': self.classes,
            'environment': self.environment,
            'exports': self.exports,
            'parameters': self.parameters
        }
        return dictionary
