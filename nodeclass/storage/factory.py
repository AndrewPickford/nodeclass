from collections import namedtuple
from .exceptions import InvalidResource, InvalidUri
from .filesystem import FileSystemClasses, FileSystemNodes
from .gitrepo import GitRepoClasses, GitRepoNodes
from .loader import KlassLoader, NodeLoader
from .yaml import Yaml

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Tuple
    from ..settings import ConfigDict
    from .uri import Uri
    StorageCache = Dict[str, Any]

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
    def klass_loader(cls, classes_uri: 'ConfigDict', cache: 'Optional[StorageCache]' = None) -> 'KlassLoader':
        def get_resource(uri: 'ConfigDict'):
            resource = uri['resource']
            if resource not in cls.storage_classes:
                raise InvalidResource(uri, resource, 'classes')
            return resource

        def get_storage(resource: 'str', uri: 'ConfigDict', cache: 'Optional[StorageCache]'):
            try:
                return cls.storage_classes[resource].storage(classes_uri=uri, cache=cache, **cls.storage_classes[resource].kwargs)
            except InvalidUri as exception:
                exception.uri = uri
                exception.section = 'classes'
                raise

        storages = []
        default_uri = { k: v for k, v in classes_uri.items() if k != 'env_overrides' }
        if 'env_overrides' in classes_uri:
            for env in classes_uri['env_overrides']:
                for env_name, env_uri in env.items():
                    mangled_uri = { k: v for k, v in default_uri.items() }
                    mangled_uri.update(env_uri)
                    resource = get_resource(mangled_uri)
                    mangled_uri = cls.storage_classes[resource].storage.clean_uri(mangled_uri)
                    storage = get_storage(resource, mangled_uri, cache)
                    storages.append( (env_name, storage) )
        default_resource = get_resource(default_uri)
        default_storage = get_storage(default_resource, default_uri, cache)
        storages.append( ('*', default_storage) )
        return KlassLoader(storages)

    @classmethod
    def node_loader(cls, nodes_uri: 'ConfigDict', cache: 'Optional[StorageCache]' = None) -> 'NodeLoader':
        resource = nodes_uri['resource']
        if resource not in cls.storage_nodes:
            raise InvalidResource(nodes_uri, resource, 'nodes')
        try:
            storage = cls.storage_nodes[resource].storage(nodes_uri=nodes_uri, cache=cache, **cls.storage_classes[resource].kwargs)
        except InvalidUri as exception:
            exception.uri = nodes_uri
            exception.section = 'nodes'
            raise
        return NodeLoader(storage)

    @classmethod
    def loaders(cls, uri: 'Uri') -> 'Tuple[KlassLoader, NodeLoader]':
        ''' Make the class and node loader objects

            uri: location of classes and nodes data in several formats (see examples)
            returns: tuple of a KlassLoader and a NodeLoader object

            ** Examples **

            * From single string:
            >>> from nodeclass.storage.factory import Factory
            >>> klass_loader, node_loader = Factory.loaders('yaml_fs:/path/to/basedir')
            >>> klass_loader
            KlassLoader(yaml_fs:/path/to/basedir/classes)
            >>> node_loader
            NodeLoader(yaml_fs:/path/to/basedir/nodes)

            * From dict with classes and nodes strings:
            >>> from nodeclass.storage.factory import Factory
            >>> klass_loader, node_loader = Factory.loaders({ 'classes': 'yaml_fs:/path/to/classes', 'nodes': 'yaml_fs:/path/to/nodes' })
            >>> klass_loader
            KlassLoader(yaml_fs:/path/to/classes)
            >>> node_loader
            NodeLoader(yaml_fs:/path/to/nodes)
        '''

        cache: 'StorageCache' = {}
        klass_loader = cls.klass_loader(uri.classes_uri, cache)
        node_loader = cls.node_loader(uri.nodes_uri, cache)
        return klass_loader, node_loader
