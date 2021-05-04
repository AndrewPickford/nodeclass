class ProtoKlass:
    '''
    '''

    def __init__(self, name, class_dict, url):
        self.name = name
        self.url = url
        # It is possible for classes, applications, exports and parameters in the yaml
        # to be None. Change these to an empty list or dict as appropriate.
        self.classes = class_dict.get('classes', None) or []
        self.applications = class_dict.get('applications', None) or []
        self.exports = class_dict.get('exports', None) or {}
        self.parameters = class_dict.get('parameters', None) or {}
        # only node classes have an environment
        self.environment = class_dict.get('environment', None)
        return

    def __repr__(self):
        return '{0}(name={1}, url={2}, klass={3})'.format(self.__class__.__name__,
                   repr(self.name), repr(self.environment), repr(self.klass))

    def __str__(self):
        return '(name={0}, environment={1}, klass={2})'.format(str(self.name),
                   str(self.environment), str(self.klass))
