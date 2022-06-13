from ..exceptions import ConfigError, FileError

class ClassNotFound(FileError):
    def __init__(self, classname, urls):
        super().__init__()
        self.classname = classname
        self.urls = urls
        self.environment = None

    def message(self):
        return super().message() + \
               [ 'Class not found',
                 'Class: {0}'.format(self.classname),
                 'Environment: {0}'.format(self.environment) ]


class DuplicateClass(FileError):
    def __init__(self, classname, duplicates):
        super().__init__()
        self.classname = classname
        self.duplicates = duplicates
        self.environment = None

    def message(self):
        return super().message() + \
               [ 'Duplicate class definitions',
                 'Class: {0}'.format(self.classname),
                 'Environment: {0}'.format(self.environment),
                 'Duplicates:' ] + \
               [ url for url in self.duplicates ]


class DuplicateNode(FileError):
    def __init__(self, node, storage, duplicates):
        super().__init__()
        self.node = node
        self.storage = storage
        self.duplicates = duplicates

    def message(self):
        return super().message() + \
               [ 'Duplicate node definitions',
                 'Duplicates:' ] + \
               [ url for url in self.duplicates ]


class InvalidUri(ConfigError):
    def __init__(self, uri, details):
        super().__init__()
        self.uri = uri
        self.details = details

    def message(self):
        return super().message() + \
               [ 'Invalid uri: {0}'.format(self.uri),
                 self.details ]


class NodeNotFound(FileError):
    def __init__(self, nodename, storage):
        super().__init__()
        self.node = nodename
        self.storage = storage

    def message(self):
        return super().message() + [ 'No such node' ]


class PygitConfigError(ConfigError):
    def __init__(self, details):
        super().__init__()
        self.details = details

    def message(self):
        return super().message() + \
               [ 'Pygit config error', self.details ]


class FileUnhandledError(FileError):
    def __init__(self, exception, node=None, storage=None, url=None, environment=None):
        super().__init__()
        self.exception = exception
        self.node = node
        self.storage = storage
        self.url = url
        self.environment = environment

    def message(self):
        return super().message() + \
               [ 'Unhandled error during interpolation',
                 'Url: {0}'.format(self.url),
                 'Envronment: {0}'.format(self.environment),
                 str(self.exception) ] + \
               self.traceback() +\
               self.traceback_other(self.exception)
