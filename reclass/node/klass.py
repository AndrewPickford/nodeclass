from ..value.make import make_value_dictionary
from .protoklass import ProtoKlass

class Klass:
    ''' A reclass class.
    '''

    def __init__(self, proto, parameters, exports):
        '''
        proto: a ProtoKlass object
        parameters: a Value wrapped TopDictionary of parameters
        exports: a Value wrapped TopDictionary of exports
        '''
        self.name = proto.name
        self.url = proto.url
        self.classes = proto.classes
        self.applications = proto.applications
        self.exports = exports
        self.parameters = parameters

    def __repr__(self):
        return '{0}(name={1}, url={2}, classes={3}, applications={4}, exports={5}, parameters={6})'.format(
                   self.__class__.__name__, repr(self.name), repr(self.url), repr(self.classes),
                   repr(self.applications), repr(self.exports), repr(self.parameters))

    def __str__(self):
        return '(name={0}, url={1}, classes={2}, applications={3}, exports={4}, parameters={5})'.format(
                   str(self.name), str(self.url), str(self.classes), str(self.applications),
                   str(self.exports), str(self.parameters))

    @staticmethod
    def from_class_dict(name, class_dict, url):
        proto = ProtoKlass(name, class_dict, url)
        parameters = make_value_dictionary(proto.parameters, proto.url)
        exports = make_value_dictionary(proto.exports, proto.url)
        parameters.freeze()
        exports.freeze()
        return Klass(proto, parameters, exports), proto.environment
