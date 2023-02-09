from ..exceptions import ConfigError, FileError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Sequence
    from ..utils.url import Url
    from ..exceptions import MessageList

class ClassNotFound(FileError):
    def __init__(self, classname: 'str', urls: 'Sequence[Url]'):
        super().__init__()
        self.classname = classname
        self.urls = urls

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Class {0} (env: {1}) not found in {2}'.format(self.classname, self.environment, self.storage),
                 'Valid urls:', 2 ] +\
               list(self.urls)


class DuplicateClass(FileError):
    def __init__(self, classname: 'str', duplicates: 'Sequence[Url]'):
        super().__init__()
        self.classname = classname
        self.duplicates = duplicates

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Duplicate class definitions for {0} (env: {1}):'.format(self.classname, self.environment), 2 ] + \
               [ url for url in self.duplicates ]


class DuplicateNode(FileError):
    def __init__(self, node: 'str', storage: 'str', duplicates: 'Sequence[Url]'):
        super().__init__()
        self.node = node
        self.storage = storage
        self.duplicates = duplicates

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Duplicate node definitions:', 2 ] + \
               [ url for url in self.duplicates ]


class InvalidUri(ConfigError):
    def __init__(self, uri, location=None, section=None):
        super().__init__()
        self.uri = uri
        self.location = location
        self.section = section

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Error in {0}:'.format(self.location), 2 ]


class UriFormatError(InvalidUri):
    def __init__(self, uri):
        super().__init__(uri)

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Invalid uri: {0}'.format(self.uri) ]


class InvalidUriOption(InvalidUri):
    def __init__(self, uri, option):
        super().__init__(uri)
        self.option = option

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'uri:{0} - invalid option: {1}'.format(self.section, self.option) ]


class RequiredUriOptionMissing(InvalidUri):
    def __init__(self, uri, option, section=None):
        super().__init__(uri, section=section)
        self.option = option

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'uri:{0} - required option {1} missing'.format(self.section, self.option) ]

class InvalidResource(InvalidUri):
    def __init__(self, uri, resource, section):
        super().__init__(uri, section=section)
        self.resource = resource

    def message(self) -> 'MessageList':
        return super().message() +\
               [ 'uri:{0}:resource - invalid value: {1}'.format(self.section, self.resource) ]


class BadNodeBranch(InvalidUri):
    def __init__(self, branch):
        super().__init__(uri=None)
        self.branch = branch

    def message(self) -> 'MessageList':
        return super().message() +\
               [ 'uri:nodes:repo: {0}'.format(self.uri.get('repo', None)),
                 'uri:nodes:branch - no such branch {0}'.format(self.branch) ]


class NodeNotFound(FileError):
    def __init__(self, nodename: 'str', storage: 'str'):
        super().__init__()
        self.node = nodename
        self.storage = storage

    def message(self) -> 'MessageList':
        return super().message() + [ 'Node not found in {0}'.format(self.storage) ]


class InvalidNodeName(FileError):
    def __init__(self, nodename: 'str', storage: 'str'):
        super().__init__()
        self.node = nodename
        self.storage = storage

    def message(self) -> 'MessageList':
        return super().message() + [ 'Invalid node name: {0} ({1})'.format(self.node, self.storage) ]


class PygitConfigError(ConfigError):
    def __init__(self, details):
        super().__init__()
        self.details = details

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Pygit config error', self.details ]


class FileParsingError(FileError):
    def __init__(self, exception):
        super().__init__()
        self.exception = exception
        self.url = None

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'url: {0}'.format(self.url) ]


class YamlParsingError(FileParsingError):
    def __init__(self, exception):
        super().__init__(exception)

    def message(self) -> 'MessageList':
        details = [ d.strip() for d in str(self.exception).split('\n') ]
        return super().message() + \
               [ 'yaml parsing error:' ] + [ 2 ] + details


class FileUnhandledError(FileError):
    def __init__(self, exception: 'Exception', node: 'Optional[str]' = None, storage: 'Optional[str]' = None, url: 'Optional[Url]' = None, environment: 'Optional[str]' = None):
        super().__init__()
        self.exception = exception
        self.node = node
        self.storage = storage
        self.url = url
        self.environment = environment

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Unhandled error during interpolation',
                 'Url: {0}'.format(self.url),
                 'Envronment: {0}'.format(self.environment),
                 str(self.exception) ] + \
               self.traceback() + \
               self.traceback_other(self.exception)


class NoMatchingBranch(FileError):
    def __init__(self, branch: 'str', repo: 'str'):
        super().__init__()
        self.branch = branch
        self.repo = repo

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'In repo: {0}'.format(self.repo),
                 'No branch {0} for environment {1}'.format(self.branch, self.environment) ]
