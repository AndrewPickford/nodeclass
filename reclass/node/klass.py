class Klass:
    '''
    Holds a representation of a reclass class
    '''

    def __init__(self, data, uri):
        '''
        data: dict of data from yaml file
        uri : location of class (plain file + file name, git repo + file name, ...)
        '''
        self.klasses = data.get('classes', None)
        self.applications = data.get('applications', None)
        self.exports = data.get('exports', None)
        self.parameters = data.get('parameters', None)
        self.uri = uri
