from collections import namedtuple
from .exceptions import InvalidResource, InvalidUri, RequiredUriOptionMissing, UriFormatError
from .filesystem import FileSystemClasses, FileSystemNodes
from .gitrepo import GitRepoClasses, GitRepoNodes
from .loader import KlassLoader, NodeLoader
from .yaml import Yaml

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Dict
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
    def klass_loader(cls, uri, cache=None):
        def get_resource(uri):
            if isinstance(uri, str):
                resource, _ = uri.split(':', 1)
            elif 'resource' not in uri:
                raise RequiredUriOptionMissing(uri, 'resource', section='classes')
            else:
                resource = uri['resource']
            if resource not in cls.storage_classes:
                raise InvalidResource(uri, resource, 'classes')
            return resource

        def get_storage(resource, uri, cache):
            try:
                return cls.storage_classes[resource].storage(uri=uri, cache=cache, **cls.storage_classes[resource].kwargs)
            except InvalidUri as exception:
                exception.uri = uri
                exception.section = 'classes'
                raise

        storages = []
        if isinstance(uri, str):
            default_uri = uri
        else:
            default_uri = { k: v for k, v in uri.items() if k != 'env_overrides' }
            if 'env_overrides' in uri:
                for env in uri['env_overrides']:
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
    def node_loader(cls, uri, cache=None):
        if isinstance(uri, str):
            resource, _ = uri.split(':', 1)
        elif 'resource' not in uri:
            raise RequiredUriOptionMissing(uri, 'resource', section='nodes')
        else:
            resource = uri['resource']
        if resource not in cls.storage_nodes:
            raise InvalidResource(uri, resource, 'nodes')
        try:
            nodes = cls.storage_nodes[resource].storage(uri=uri, cache=cache, **cls.storage_classes[resource].kwargs)
        except InvalidUri as exception:
            exception.uri = uri
            exception.section = 'nodes'
            raise
        return NodeLoader(nodes)

    @classmethod
    def loaders(cls, uri):
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
        if isinstance(uri, str):
            try:
                resource, _ = uri.split(':', 1)
            except ValueError:
                raise UriFormatError(uri)
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
        raise UriFormatError(uri)
