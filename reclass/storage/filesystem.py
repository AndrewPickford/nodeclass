import collections
import contextlib
import os
from ..exceptions import ReclassRuntimeError
from .exceptions import ClassNotFoundError, DuplicateClassError, DuplicateNodeError, NodeNotFoundError

class FileSystem:
    '''
    '''

    ignore_options = [ 'resource' ]
    required_options = [ 'path' ]
    valid_options = required_options

    @classmethod
    def validate_uri(cls, uri):
        def validate_option(option):
            if option not in cls.valid_options:
                raise ReclassRuntimeError('Invalid filesystem option {0}'.format(option))
            return option

        options = { validate_option(option): value for option, value in uri.items() if option not in cls.ignore_options }
        for required in cls.required_options:
            if required not in options:
                raise ReclassRuntimeError('Required filesystem option {0} not present'.format(required))
        return options

    @classmethod
    def uri_from_string(cls, uri_string):
        resource, path = uri_string.split(':', 1)
        return { 'resource': resource, 'path': path }

    @classmethod
    def from_uri(cls, uri, cache):
        if isinstance(uri, str):
            uri = cls.uri_from_string(uri)
        uri_valid = cls.validate_uri(uri)
        if cache is None:
            return cls(**uri_valid), uri
        name = 'fs {0}'.format(uri['path'])
        if name not in cache:
            cache[name] = cls(**uri_valid)
        return cache[name], uri

    def __init__(self, path):
        self.basedir = os.path.abspath(path)

    def __contains__(self, path):
        fullpath = os.path.join(self.basedir, path)
        return os.path.exists(fullpath)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.basedir)

    def __str__(self):
        return '{0}'.format(self.basedir)

    def get(self, path):
        fullpath = os.path.join(self.basedir, path)
        with open(fullpath) as file:
            return file.read()

    @contextlib.contextmanager
    def open(self, path):
        fullpath = os.path.join(self.basedir, path)
        with open(fullpath) as file:
            yield file


class FileSystemClasses:
    '''
    '''

    @classmethod
    def subpath(cls, uri):
        if isinstance(uri, str):
            uri = FileSystem.uri_from_string(uri)
        uri['path'] = os.path.join(uri['path'], 'classes')
        return uri

    def __init__(self, uri, format, cache=None):
        self.file_system, uri = FileSystem.from_uri(uri, cache)
        self.format = format
        self.resource = uri['resource']
        self.path = uri['path']

    def _path_url(self, path):
        return '{0}:{1}'.format(self.resource, os.path.join(self.path, path))

    def name_to_path(self, name):
        base = name.replace('.', '/')
        basepaths = [ '{0}'.format(base), '{0}/init'.format(base) ]
        paths = [ '{0}.{1}'.format(path, ext) for ext in self.format.extensions for path in basepaths ]
        present = [ path for path in paths if path in self.file_system ]
        if len(present) == 1:
            return present[0]
        elif len(present) > 1:
            duplicates = [ self._path_url(duplicate) for duplicate in present ]
            raise DuplicateClassError(name, duplicates)
        raise ClassNotFoundError(name, [ self._path_url(path) for path in paths ])

    def get(self, name, environment):
        path = self.name_to_path(name)
        try:
            if self.format.load:
                with self.file_system.open(path) as file:
                    return self.format.load(file), self._path_url(path)
            else:
                return self.format.process(self.file_system.get(path)), self._path_url(path)
        except FileNotFoundError as exc:
            raise ClassNotFoundError(name, [ self._path_url(path) ])


class FileSystemNodes:
    '''
    '''

    @classmethod
    def subpath(cls, uri):
        if isinstance(uri, str):
            uri = FileSystem.uri_from_string(uri)
        uri['path'] = os.path.join(uri['path'], 'nodes')
        return uri

    def __init__(self, uri, format, cache=None):
        self.file_system, uri = FileSystem.from_uri(uri, cache)
        self.format = format
        self.resource = uri['resource']
        self.path = uri['path']
        self.node_map = self._make_node_map()

    def __str__(self):
        return '{0}:{1}'.format(self.resource, self.file_system)

    def _make_node_map(self):
        node_map = collections.defaultdict(list)
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            for file in filenames:
                path = os.path.join(dirpath, file)
                nodename, extension = os.path.splitext(file)
                if extension[1:] in self.format.extensions:
                    node_map[nodename].append(os.path.relpath(path, start=self.path))
        return node_map

    def _path_url(self, path):
        return '{0}:{1}'.format(self.resource, os.path.join(self.path, path))

    def get(self, name):
        if name not in self.node_map:
            raise NodeNotFoundError(name, str(self))
        elif len(self.node_map[name]) != 1:
            duplicates = [ self._path_url(duplicate) for duplicate in self.node_map[name] ]
            raise DuplicateNodeError(name, str(self), duplicates)
        try:
            path = self.node_map[name][0]
            if self.format.load:
                with self.file_system.open(path) as file:
                    return self.format.load(file), self._path_url(path)
            else:
                return self.format.process(self.file_system.get(path)), self._path_url(path)
        except FileNotFoundError as exc:
            raise NodeNotFoundError(name, str(self))
