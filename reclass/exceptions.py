import traceback

class ReclassError(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return '\n'.join(self.message())

    def message(self):
        return []

    def traceback(self):
        return [ '\nTraceback:' ] + [ i.strip() for i in traceback.format_tb(self.__traceback__) ]


class ConfigError(ReclassError):
    def __init__(self):
        super().__init__()

    def message(self):
        return [ 'Configuration Error' ]


class ProcessError(ReclassError):
    def __init__(self):
        super().__init__()
        self.node = None
        self.url = None
        self.hierarchy_type = None
        self.path = None
        self.reverse_path = []

    def message(self):
        from .utils.path import Path
        if len(self.reverse_path) > 0:
            self.path = Path.fromlist(self.reverse_path[::-1])
        return [ 'Process error',
                 'Node: {0}'.format(self.node),
                 'Url: {0}'.format(self.url),
                 'Hierarchy: {0}'.format(self.hierarchy_type),
                 'Path: {0}'.format(self.path) ]

class FileError(ReclassError):
    def __init__(self):
        super().__init__()
        self.node = None
        self.storage = None

    def message(self):
        return [ 'File error',
                 'Node: {0}'.format(self.node),
                 'Storage: {0}'.format(self.storage) ]


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
