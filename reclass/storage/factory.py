from collections import namedtuple
from ..exceptions import ReclassRuntimeError
from .filesystem import FileSystemClasses, FileSystemNodes
from .loader import KlassLoader, NodeLoader
from .yaml import Yaml

StorageType = namedtuple('StorageType', ['storage', 'kwargs'])

class Factory:
    storage_classes = {
        'yaml_fs': StorageType(FileSystemClasses, {'file_format': Yaml})
    }

    storage_nodes = {
        'yaml_fs': StorageType(FileSystemNodes, {'file_format': Yaml})
    }

    @staticmethod
    def join_path(base_path, sub_path):
        if base_path[-1] == '/':
            return '{0}{1}'.format(base_path, sub_path)
        return '{0}/{1}'.format(base_path, sub_path)

    @classmethod
    def klass_loader(cls, resource, path):
        if resource not in cls.storage_classes:
            raise ReclassRuntimeError('Unknown storage type {0}'.format(resource))
        klasses = cls.storage_classes[resource].storage(path=path, **cls.storage_classes[resource].kwargs)
        return KlassLoader(klasses)

    @classmethod
    def node_loader(cls, resource, path):
        if resource not in cls.storage_nodes:
            raise ReclassRuntimeError('Unknown storage type {0}'.format(resource))
        nodes = cls.storage_nodes[resource].storage(path=path, **cls.storage_classes[resource].kwargs)
        return NodeLoader(nodes)

    @classmethod
    def loaders(cls, uri):
        ''' Return a KlassLoader and a NodeLoader objects

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

        if isinstance(uri, str):
            try:
                resource, path = uri.split(':', 1)
            except ValueError:
                raise ReclassRuntimeError('Invalid uri: {0}'.format(uri))
            klass_loader = cls.klass_loader(resource, cls.join_path(path, 'classes'))
            node_loader = cls.node_loader(resource, cls.join_path(path, 'nodes'))
            return klass_loader, node_loader
        elif isinstance(uri, dict):
            if 'classes' in uri and 'nodes' in uri:
                if isinstance(uri['classes'], str):
                    try:
                        resource, path = uri['classes'].split(':', 1)
                    except ValueError:
                        raise ReclassRuntimeError('Invalid uri: {0}'.format(uri['classes']))
                    klass_loader = cls.klass_loader(resource, path)
                else:
                    klass_loader = cls.klass_loader(**uri['classes'])
                if isinstance(uri['nodes'], str):
                    try:
                        resource, path = uri['nodes'].split(':', 1)
                    except ValueError:
                        raise ReclassRuntimeError('Invalid uri: {0}'.format(uri['classes']))
                    node_loader = cls.node_loader(resource, path)
                else:
                    node_loader = cls.node_loader(**uri['nodes'])
                return klass_loader, node_loader
        raise ReclassRuntimeError('unable to make classes and nodes loaders from uri: {0}', uri)
