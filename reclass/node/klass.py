from collections import namedtuple
from ..value.hierarchy import Hierarchy

KlassID = namedtuple('KlassID', ['name', 'environment'])

class Klass:
    ''' A reclass class.
    '''

    @staticmethod
    def from_class_dict(name, class_dict, url):
        # It is possible for classes, applications, exports and parameters in the yaml
        # to be None. Change these to an empty list or dict as appropriate.
        applications = class_dict.get('applications', None) or []
        classes = class_dict.get('classes', None) or []
        exports = class_dict.get('exports', None) or {}
        parameters = class_dict.get('parameters', None) or {}
        exports = Hierarchy.from_dict(exports, url)
        parameters = Hierarchy.from_dict(parameters, url)
        exports.freeze()
        parameters.freeze()
        return Klass(name, applications, classes, exports, parameters, url)

    def __init__(self, name, applications, classes, exports, parameters, url):
        '''
        name: class name
        applications: list of applications
        classes: list of classes
        exports: Hierarchy of exports
        parameters: Hierarchy of parameters
        url:
        '''
        self.name = name
        self.applications = applications
        self.classes = classes
        self.exports = exports
        self.parameters = parameters
        self.url = url

    def __repr__(self):
        return '{0}(name={1}, url={2}, classes={3}, applications={4}, exports={5}, parameters={6})'.format(
                   self.__class__.__name__, repr(self.name), repr(self.url), repr(self.classes),
                   repr(self.applications), repr(self.exports), repr(self.parameters))

    def __str__(self):
        return '(name={0}, url={1}, classes={2}, applications={3}, exports={4}, parameters={5})'.format(
                   str(self.name), str(self.url), str(self.classes), str(self.applications),
                   str(self.exports), str(self.parameters))
