class Klass:
    ''' A reclass class.
    '''

    def __init__(self, class_dict, url):
        '''
        class_data: dict of reclass data
        url : location of class (plain file + file name, git repo + file name, ...)
        '''
        self.classes = class_dict.get('classes', [])
        self.applications = class_dict.get('applications', [])
        self.exports = class_dict.get('exports', {})
        self.parameters = class_dict.get('parameters', {})
        self.url = url

    def __repr__(self):
        return '{0}(url={1}, classes={2}, applications={3}, exports={4}, parameters={5})'.format(
                   self.__class__.__name__, repr(self.url), repr(self.classes),
                   repr(self.applications), repr(self.exports), repr(self.parameters))

    def __str__(self):
        return '(url={0}, classes={1}, applications={2}, exports={3}, parameters={4})'.format(
                   str(self.url), str(self.classes), str(self.applications),
                   str(self.exports), str(self.parameters))
