from ..exceptions import ConfigError, FileError

class ClassNotFound(FileError):
    def __init__(self, classname, urls):
        super().__init__()
        self.classname = classname
        self.urls = urls
        self.environment = None

    def message(self):
        return super().message() + \
               [ 'Class {0} (env: {1}) not found in {2}'.format(self.classname, self.environment, self.storage),
                 'Valid urls:', 2 ] +\
               self.urls


class DuplicateClass(FileError):
    def __init__(self, classname, duplicates):
        super().__init__()
        self.classname = classname
        self.duplicates = duplicates
        self.environment = None

    def message(self):
        return super().message() + \
               [ 'Duplicate class definitions for {0} (env: {1}):'.format(self.classname, self.environment), 2 ] + \
               [ url for url in self.duplicates ]


class DuplicateNode(FileError):
    def __init__(self, node, storage, duplicates):
        super().__init__()
        self.node = node
        self.storage = storage
        self.duplicates = duplicates

    def message(self):
        return super().message() + \
               [ 'Duplicate node definitions:', 2 ] + \
               [ url for url in self.duplicates ]


class InvalidUri(ConfigError):
    def __init__(self, uri, details, location=None):
        super().__init__()
        self.uri = uri
        self.details = details
        self.location = location

    def message(self):
        return super().message() + \
               [ 'Invalid uri: {0}'.format(self.details),
                 'in {0}'.format(self.location) ]


class NodeNotFound(FileError):
    def __init__(self, nodename, storage):
        super().__init__()
        self.node = nodename
        self.storage = storage

    def message(self):
        return super().message() + [ 'Node not found in {0}'.format(self.storage) ]


class PygitConfigError(ConfigError):
    def __init__(self, details):
        super().__init__()
        self.details = details

    def message(self):
        return super().message() + \
               [ 'Pygit config error', self.details ]


class FileParsingError(FileError):
    def __init__(self, exception):
        super().__init__()
        self.exception = exception
        self.url = None

    def message(self):
        return super().message() + \
               [ 'url: {0}'.format(self.url) ]


class YamlParsingError(FileParsingError):
    def __init__(self, exception):
        super().__init__(exception)

    def message(self):
        details = [ 2 ] + [ d.strip() for d in str(self.exception).split('\n') ]
        return super().message() + \
               [ 'yaml parsing error:' ] + details


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
