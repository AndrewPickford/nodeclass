from collections import namedtuple
from ..exceptions import ReclassRuntimeError
from .filesystem import FileSystemClasses, FileSystemNodes
from .gitrepo import GitRepoClasses, GitRepoNodes
from .loader import KlassLoader, NodeLoader
from .yaml import Yaml

StorageType = namedtuple('StorageType', ['storage', 'kwargs'])

class Factory:
    storage_classes = {
        'yaml_fs': StorageType(FileSystemClasses, {'format': Yaml}),
        'yaml_git': StorageType(GitRepoClasses, {'format': Yaml}),
    }

    storage_nodes = {
        'yaml_fs': StorageType(FileSystemNodes, {'format': Yaml}),
        'yaml_git': StorageType(GitRepoNodes, {'format': Yaml}),
    }

    @classmethod
    def klass_loader(cls, uri, cache=None):
        if isinstance(uri, str):
            resource, _ = uri.split(':', 1)
        elif 'resource' not in uri:
            raise ReclassRuntimeError('Resource not defined in {0}'.format(uri))
        else:
            resource = uri['resource']
        if resource not in cls.storage_classes:
            raise ReclassRuntimeError('Unknown storage type {0}'.format(resource))
        klasses = cls.storage_classes[resource].storage(uri=uri, cache=cache, **cls.storage_classes[resource].kwargs)
        return KlassLoader(klasses)

    @classmethod
    def node_loader(cls, uri, cache=None):
        if isinstance(uri, str):
            resource, _ = uri.split(':', 1)
        elif 'resource' not in uri:
            raise ReclassRuntimeError('Resource not defined in {0}'.format(uri))
        else:
            resource = uri['resource']
        if resource not in cls.storage_nodes:
            raise ReclassRuntimeError('Unknown storage type {0}'.format(resource))
        nodes = cls.storage_nodes[resource].storage(uri=uri, cache=cache, **cls.storage_classes[resource].kwargs)
        return NodeLoader(nodes)

    @classmethod
    def loaders(cls, uri):
        ''' Make the class and node loader objects

            uri: location of classes and nodes data in several formats (see examples)
            returns: tuple of a KlassLoader and a NodeLoader object

            ** Examples **

            * From single string:
            >>> from reclass.storage.factory import Factory
            >>> klass_loader, node_loader = Factory.loaders('yaml_fs:/path/to/basedir')
            >>> klass_loader
            KlassLoader(yaml_fs:/path/to/basedir/classes)
            >>> node_loader
            NodeLoader(yaml_fs:/path/to/basedir/nodes)

            * From dict with classes and nodes strings:
            >>> from reclass.storage.factory import Factory
            >>> klass_loader, node_loader = Factory.loaders({ 'classes': 'yaml_fs:/path/to/classes', 'nodes': 'yaml_fs:/path/to/nodes' })
            >>> klass_loader
            KlassLoader(yaml_fs:/path/to/classes)
            >>> node_loader
            NodeLoader(yaml_fs:/path/to/nodes)
        '''

        cache = {}
        if isinstance(uri, str):
            try:
                resource, _ = uri.split(':', 1)
            except ValueError:
                raise ReclassRuntimeError('Invalid uri: {0}'.format(uri))
            klass_uri = cls.storage_classes[resource].storage.subpath(uri)
            node_uri = cls.storage_nodes[resource].storage.subpath(uri)
            klass_loader = cls.klass_loader(klass_uri, cache)
            node_loader = cls.node_loader(node_uri, cache)
            return klass_loader, node_loader
        elif isinstance(uri, dict):
            if 'classes' in uri and 'nodes' in uri:
                klass_loader = cls.klass_loader(uri['classes'], cache)
                node_loader = cls.node_loader(uri['nodes'], cache)
                return klass_loader, node_loader
        raise ReclassRuntimeError('unable to make classes and nodes loaders from uri: {0}'.format(uri))
