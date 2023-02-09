import collections
import contextlib
import os
from ..utils.url import FileUrl
from .exceptions import ClassNotFound, DuplicateClass, DuplicateNode, FileParsingError, InvalidUriOption, NodeNotFound, RequiredUriOptionMissing

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Generator, List, Optional, TextIO, Tuple, Union
    from ..config_file import ConfigData
    from .factory import StorageCache
    from .format import Format


class FileSystem:
    '''
    '''

    ignored_options = [ 'resource' ]
    required_options = [ 'path' ]
    valid_options = required_options

    @classmethod
    def validate_uri(cls, uri: 'ConfigData') -> 'ConfigData':
        def validate_option(option: 'str') -> 'str':
            if option not in cls.valid_options:
                raise InvalidUriOption(uri, option)
            return option

        options = { validate_option(option): value for option, value in uri.items() if option not in cls.ignored_options }
        for required in cls.required_options:
            if required not in options:
                raise RequiredUriOptionMissing(uri, required)
        return options

    @classmethod
    def uri_from_string(cls, uri_string: 'str') -> 'ConfigData':
        resource, path = uri_string.split(':', 1)
        return { 'resource': resource, 'path': path }

    @classmethod
    def from_uri(cls, uri: 'Union[ConfigData, str]', cache: 'Optional[StorageCache]') -> 'Tuple[FileSystem, ConfigData]':
        if isinstance(uri, str):
            uri = cls.uri_from_string(uri)
        uri_valid = cls.validate_uri(uri)
        if cache is None:
            return cls(**uri_valid), uri
        name = 'fs {0}'.format(uri['path'])
        if name not in cache:
            cache[name] = cls(**uri_valid)
        if isinstance(cache[name], FileSystem):
            return cache[name], uri
        raise RuntimeError('error')

    def __init__(self, path: 'str'):
        self.basedir = os.path.abspath(path)

    def __contains__(self, path: 'str') -> 'bool':
        fullpath = os.path.join(self.basedir, path)
        return os.path.exists(fullpath)

    def __repr__(self) -> 'str':
        return '{0}({1})'.format(self.__class__.__name__, self.basedir)

    def __str__(self) -> 'str':
        return '{0}'.format(self.basedir)

    def get(self, path: 'str') -> 'str':
        fullpath = os.path.join(self.basedir, path)
        with open(fullpath) as file:
            return file.read()

    @contextlib.contextmanager
    def open(self, path: 'str') -> 'Generator[TextIO, None, None]':
        fullpath = os.path.join(self.basedir, path)
        with open(fullpath) as file:
            yield file


class FileSystemClasses:
    '''
    '''

    valid_options = FileSystem.ignored_options + FileSystem.valid_options

    @classmethod
    def clean_uri(cls, uri: 'ConfigData') -> 'ConfigData':
        return { k: v for k, v in uri.items() if k in cls.valid_options }

    @classmethod
    def subpath(cls, uri: 'Union[ConfigData, str]') -> 'ConfigData':
        if isinstance(uri, str):
            uri = FileSystem.uri_from_string(uri)
        uri['path'] = os.path.join(uri['path'], 'classes')
        return uri

    def __init__(self, uri: 'ConfigData', format: 'Format', cache: 'Optional[StorageCache]' = None):
        self.file_system, uri = FileSystem.from_uri(uri, cache)
        self.format = format
        self.resource = uri['resource']
        self.path = uri['path']

    def __str__(self) -> 'str':
        return '{0}:{1}'.format(self.resource, self.file_system)

    def _path_url(self, name: 'str', path: 'str') -> 'FileUrl':
        return FileUrl(name, self.resource, os.path.join(self.path, path))

    def name_to_path(self, name: 'str') -> 'str':
        base = name.replace('.', '/')
        basepaths = [ '{0}'.format(base), '{0}/init'.format(base) ]
        paths = [ '{0}.{1}'.format(path, ext) for ext in self.format.extensions for path in basepaths ]
        present = [ path for path in paths if path in self.file_system ]
        if len(present) == 1:
            return present[0]
        elif len(present) > 1:
            duplicates = [ self._path_url(name, duplicate) for duplicate in present ]
            raise DuplicateClass(name, duplicates)
        raise ClassNotFound(name, [ self._path_url(name, path) for path in paths ])

    def get(self, name: 'str', environment: 'str') -> 'Tuple[Dict, FileUrl]':
        path = self.name_to_path(name)
        try:
            if self.format.load:
                with self.file_system.open(path) as file:
                    return self.format.load(file), self._path_url(name, path)
            else:
                return self.format.process(self.file_system.get(path)), self._path_url(name, path)
        except FileNotFoundError:
            raise ClassNotFound(name, [ self._path_url(name, path) ])
        except FileParsingError as exception:
            exception.url = self._path_url(name, path)
            raise


class FileSystemNodes:
    '''
    '''

    @classmethod
    def subpath(cls, uri: 'Union[ConfigData, str]') -> 'ConfigData':
        if isinstance(uri, str):
            uri = FileSystem.uri_from_string(uri)
        uri['path'] = os.path.join(uri['path'], 'nodes')
        return uri

    def __init__(self, uri: 'ConfigData', format: 'Format', cache: 'Optional[StorageCache]' = None):
        self.file_system, uri = FileSystem.from_uri(uri, cache)
        self.format = format
        self.resource = uri['resource']
        self.path = uri['path']
        self.node_map = self._make_node_map()

    def __str__(self) -> 'str':
        return '{0}:{1}'.format(self.resource, self.file_system)

    def _make_node_map(self) -> 'Dict[str, List[str]]':
        node_map = collections.defaultdict(list)
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            for file in filenames:
                path = os.path.join(dirpath, file)
                nodename = self.format.mangle_name(file)
                if nodename:
                    node_map[nodename].append(os.path.relpath(path, start=self.path))
        return node_map

    def _path_url(self, name: 'str', path: 'str') -> 'FileUrl':
        return FileUrl(name, self.resource, os.path.join(self.path, path))

    def get(self, name: 'str') -> 'Tuple[Dict, FileUrl]':
        if name not in self.node_map:
            raise NodeNotFound(name, str(self))
        elif len(self.node_map[name]) != 1:
            duplicates = [ self._path_url(name, duplicate) for duplicate in self.node_map[name] ]
            raise DuplicateNode(name, str(self), duplicates)
        try:
            path = self.node_map[name][0]
            if self.format.load:
                with self.file_system.open(path) as file:
                    return self.format.load(file), self._path_url(name, path)
            else:
                return self.format.process(self.file_system.get(path)), self._path_url(name, path)
        except FileNotFoundError:
            raise NodeNotFound(name, str(self))
        except FileParsingError as exception:
            exception.url = self._path_url(name, path)
            raise
