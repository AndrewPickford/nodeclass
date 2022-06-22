import traceback

class NodeclassError(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
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

    def message(self):
        return []

    def traceback(self):
        return [ '\nTraceback:' ] + [ i.strip() for i in traceback.format_tb(self.__traceback__) ]

    def traceback_other(self, other):
        return [ '\nTraceback:' ] + [ i.strip() for i in traceback.format_tb(other.__traceback__) ]


class MultipleNodeErrors(NodeclassError):
    def __init__(self, exceptions = None):
        super().__init__()
        self.exceptions = exceptions or []

    def message(self):
        m = []
        for e in self.exceptions:
            m.append(None)
            m.extend(e.message())
            m.append('')
        return m


class ConfigError(NodeclassError):
    def __init__(self):
        super().__init__()

    def message(self):
        return [ 'Configuration Error' ]


class ProcessError(NodeclassError):
    def __init__(self):
        super().__init__()
        self.node = None

    def message(self):
        return [ 0, '--> {0}'.format(self.node), 2 ]


class InputError(ProcessError):
    def __init__(self):
        super().__init__()
        self.url = None
        self.hierarchy_type = None
        self.path = None
        self.reverse_path = []

    def message(self):
        from .utils.path import Path
        self.path = Path.fromlist(self.reverse_path[::-1])
        return super().message() + \
               [ 'Url: {0}'.format(self.url),
                 'Hierarchy: {0}'.format(self.hierarchy_type),
                 'Path: {0}'.format(self.path) ]


class InterpolationError(ProcessError):
    def __init__(self):
        super().__init__()
        self.url = None
        self.hierarchy_type = None
        self.path = None
        self.reverse_path = []

    def msg(self):
        return []

    def message(self):
        from .utils.path import Path
        if self.path == None and len(self.reverse_path) > 0:
            self.path = Path.fromlist(self.reverse_path[::-1])
        return super().message() + self.msg()


class FileError(ProcessError):
    def __init__(self):
        super().__init__()
        self.storage = None
        self.url = None

    def message(self):
        return super().message() + \
               [ 'storage: {0}'.format(self.storage) ]


class NoConfigFile(ConfigError):
    def __init__(self, filename, search_path):
        super().__init__()
        self.filename = filename
        self.search_path = search_path

    def message(self):
        return super().message() + \
               [ 'No config file ({0}) found in search path: {1}'.format(self.filename, self.search_path) ]


class UnknownConfigSetting(ConfigError):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def message(self):
        return super().message() + \
               [ 'Unknown config setting: {0}'.format(self.name) ]
