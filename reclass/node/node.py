from .klass import Klass

class Node:
    ''' A reclass node
    '''

    def __init__(self, nodename, node_dict, url, class_loader):
        '''
        nodename: full name of node
        node_dict: dict of reclass data for the node
        url: location of node file
        classes: dict like object of available classes, indexed by class name
        '''
        self.nodename = nodename
        self.nodeclass = Klass(node_dict, url)
        self.environment = node_dict.get('environment', None)
        self.classes = [ Klass({ 'parameters': self.base_parameters() }, 'base') ]
        self.classes_loaded = set()
        self.url = url
        self.load_classes(self.nodeclass.classes, class_loader)
        self.classes.append(self.nodeclass)

    def __repr__(self):
        return '{0}(url={1}, nodeclass={2}, classes={3})'.format(
                   self.__class__.__name__, repr(self.url), repr(self.nodeclass),
                   repr(self.classes))

    def __str__(self):
        return '(url={0}, nodeclass={1}, classes={2})'.format(repr(self.url),
                   repr(self.nodeclass), repr(self.classes))

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

    def load_classes(self, classes, class_loader):
        for classname in classes:
            if classname not in self.classes_loaded:
                new_class = Klass(*class_loader[classname])
                self.classes_loaded.add(classname)
                self.load_classes(new_class.classes, class_loader)
                self.classes.append(new_class)
