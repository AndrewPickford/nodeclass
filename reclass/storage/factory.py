from collections import namedtuple
from .exceptions import UnknownStorageTypeError
from .filesystem import FileSystemClasses, FileSystemNodes
from .loader import KlassLoader, NodeLoader
from .yaml import Yaml

StorageType = namedtuple('StorageType', ['storage', 'args'])

class Factory:
    storage_classes = {
        'yaml_fs': StorageType(FileSystemClasses, {'file_format': Yaml})
    }

    storage_nodes = {
        'yaml_fs': StorageType(FileSystemNodes, {'file_format': Yaml})
    }

    def __init__(self, value_factory):
        self.value_factory = value_factory

    def classes(self, uri):
        storage_name, basedir = uri.split(':')
        if storage_name in self.storage_classes:
            return self.storage_classes[storage_name].storage(basedir=basedir, **self.storage_classes[storage_name].args)
        else:
            raise UnknownStorageTypeError(storage_name, uri)

    def nodes(self, uri):
        storage_name, basedir = uri.split(':')
        if storage_name in self.storage_nodes:
            return self.storage_nodes[storage_name].storage(basedir=basedir, **self.storage_nodes[storage_name].args)
        else:
            raise UnknownStorageTypeError(storage_name, uri)

    def klass_loader(self, uri):
        classes_ = self.classes(uri)
        return KlassLoader(classes_, self.value_factory)

    def node_loader(self, uri):
        nodes_ = self.nodes(uri)
        return NodeLoader(nodes_, self.value_factory)
