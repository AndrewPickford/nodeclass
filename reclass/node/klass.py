class Klass:
    ''' A reclass class.
    '''

    def __init__(self, classname, class_dict, url):
        '''
        classname: name of the class
        class_dict: dict of reclass data
        url : location of class (plain file + file name, git repo + file name, ...)
        '''
        self.name = classname
        self.url = url
        # It is possible for classes, applications, exports and parameters in the yaml
        # to be None. Change these to an empty list or dict as appropriate.
        self.classes = class_dict.get('classes', None) or []
        self.applications = class_dict.get('applications', None) or []
        self.exports = class_dict.get('exports', None) or {}
        self.parameters = class_dict.get('parameters', None) or {}

    def __repr__(self):
        return '{0}(name={1}, url={2}, classes={3}, applications={4}, exports={5}, parameters={6})'.format(
                   self.__class__.__name__, repr(self.name), repr(self.url), repr(self.classes),
                   repr(self.applications), repr(self.exports), repr(self.parameters))

    def __str__(self):
        return '(name={0}, url={1}, classes={2}, applications={3}, exports={4}, parameters={5})'.format(
                   str(self.name), str(self.url), str(self.classes), str(self.applications),
                   str(self.exports), str(self.parameters))
