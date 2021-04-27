from collections import namedtuple
from .exceptions import UnknownStorageTypeError
from .filesystem import FileSystemClasses, FileSystemNodes
from .yaml import Yaml

StorageType = namedtuple('StorageType', ['storage', 'args'])

class Factory:
    storage_classes = {
        'yaml_fs': StorageType(FileSystemClasses, {'file_format': Yaml})
    }

    storage_nodes = {
        'yaml_fs': StorageType(FileSystemNodes, {'file_format': Yaml})
    }

    @classmethod
    def classes(cls, uri):
        storage_name, basedir = uri.split(':')
        if storage_name in cls.storage_classes:
            return cls.storage_classes[storage_name].storage(basedir=basedir, **cls.storage_classes[storage_name].args)
        else:
            raise UnknownStorageTypeError(storage_name, uri)

    @classmethod
    def nodes(cls, uri):
        storage_name, basedir = uri.split(':')
        if storage_name in cls.storage_nodes:
            return cls.storage_nodes[storage_name].storage(basedir=basedir, **cls.storage_nodes[storage_name].args)
        else:
            raise UnknownStorageTypeError(storage_name, uri)
