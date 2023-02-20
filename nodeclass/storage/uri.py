from .exceptions import RequiredUriOptionMissing, UriFormatError
from .factory import Factory

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union
    from ..config_file import ConfigDict


class Uri:
    def __init__(self, uri_config: 'Union[ConfigDict, str]', location: 'str'):
        self.classes_uri: 'ConfigDict'
        self.nodes_uri: 'ConfigDict'
        self.location = location

        if isinstance(uri_config, str):
            try:
                resource, _ = uri_config.split(':', 1)
            except ValueError:
                raise UriFormatError(uri_config)
            try:
                classes_uri = Factory.storage_classes[resource].storage.subpath(uri_config)
                nodes_uri = Factory.storage_nodes[resource].storage.subpath(uri_config)
            except KeyError:
                raise UriFormatError(uri_config)
        elif isinstance(uri_config, dict):
            try:
                classes_uri = uri_config['classes']
                nodes_uri = uri_config['nodes']
            except KeyError:
                raise UriFormatError(uri_config)
        else:
            raise UriFormatError(uri_config)

        if isinstance(classes_uri, str):
            try:
                resource, _ = classes_uri.split(':', 1)
            except ValueError:
                raise UriFormatError(uri_config)
            try:
                self.classes_uri = Factory.storage_classes[resource].storage.uri_from_string(classes_uri)
            except KeyError:
                raise UriFormatError(uri_config)
        elif isinstance(classes_uri, dict):
            if 'resource' not in classes_uri:
                raise RequiredUriOptionMissing(classes_uri, 'resource', section='classes')
            self.classes_uri = classes_uri
        else:
            raise UriFormatError(uri_config)

        if isinstance(nodes_uri, str):
            try:
                resource, _ = nodes_uri.split(':', 1)
            except ValueError:
                raise UriFormatError(uri_config)
            try:
                self.nodes_uri = Factory.storage_nodes[resource].storage.uri_from_string(nodes_uri)
            except KeyError:
                raise UriFormatError(uri_config)
        elif isinstance(nodes_uri, dict):
            if 'resource' not in nodes_uri:
                raise RequiredUriOptionMissing(nodes_uri, 'resource', section='nodes')
            self.nodes_uri = nodes_uri
        else:
            raise UriFormatError(uri_config)
