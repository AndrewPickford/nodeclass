import traceback

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, List, Optional
    from .utils.url import Url
    MessageList = List[Any]


class NodeclassError(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self) -> 'str':
        mess = []
        indent = 0
        for m in self.message():
            if m is None:
                indent = 0
            elif isinstance(m, int):
                indent = indent + m
            else:
                mess.append('{0}{1}'.format(' '*indent, m))
        return '\n'.join(mess)

    def message(self) -> 'MessageList':
        return []

    def traceback(self) -> 'MessageList':
        return [ '\nTraceback:' ] + [ i.strip() for i in traceback.format_tb(self.__traceback__) ]

    def traceback_other(self, other: 'Exception') -> 'MessageList':
        return [ '\nTraceback:' ] + [ i.strip() for i in traceback.format_tb(other.__traceback__) ]


class MultipleNodeErrors(NodeclassError):
    def __init__(self, exceptions = None):
        super().__init__()
        self.exceptions: List = exceptions or []

    def message(self) -> 'MessageList':
        m: 'MessageList' = []
        for e in self.exceptions:
            m.append(None)
            m.extend(e.message())
            m.append('')
        return m


class ConfigError(NodeclassError):
    def __init__(self):
        super().__init__()

    def message(self) -> 'MessageList':
        return []


class ProcessError(NodeclassError):
    def __init__(self):
        super().__init__()
        self.node = None

    def message(self) -> 'MessageList':
        return [ '--> {0}'.format(self.node), 2 ]


class InputError(ProcessError):
    def __init__(self):
        super().__init__()
        self.url = None
        self.category = None
        self.path = None
        self.reverse_path = []

    def _get_path(self):
        from .utils.path import Path
        if self.path == None and len(self.reverse_path) > 0:
            self.path = Path.fromlist(self.reverse_path[::-1])

    def message(self) -> 'MessageList':
        self._get_path()
        return super().message() + \
               [ 'Url: {0}'.format(self.url),
                 'Category: {0}'.format(self.category),
                 'Path: {0}'.format(self.path) ]


class InterpolationError(ProcessError):
    def __init__(self):
        super().__init__()
        self.url = None
        self.category = None
        self.path = None
        self.reverse_path = []

    def _get_path(self):
        from .utils.path import Path
        if self.path == None and len(self.reverse_path) > 0:
            self.path = Path.fromlist(self.reverse_path[::-1])

    def msg(self) -> 'MessageList':
        return []

    def message(self) -> 'MessageList':
        self._get_path()
        return super().message() + self.msg()


class FileError(ProcessError):
    def __init__(self):
        super().__init__()
        self.storage: 'Optional[str]' = None
        self.url: 'Optional[Url]' = None
        self.environment: 'Optional[str]' = None

    def message(self) -> 'MessageList':
        return super().message()


class NoConfigFile(ConfigError):
    def __init__(self, filename, search_path):
        super().__init__()
        self.filename = filename
        self.search_path = search_path

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'No config file, {0}, found in search path: {1}'.format(self.filename, ', '.join(self.search_path)) ]


class ConfigFileParseError(ConfigError):
    def __init__(self, filename, exception):
        super().__init__()
        self.filename = filename
        self.exception = exception

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Error parsing config file {0}'.format(self.filename),
                 str(self.exception) ]


class UnknownConfigSetting(ConfigError):
    def __init__(self, name, location=None):
        super().__init__()
        self.name = name
        self.location = location

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Unknown config setting: {0}, in {1}'.format(self.name, self.location) ]
