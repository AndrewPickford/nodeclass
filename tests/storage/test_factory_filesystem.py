import os
import pytest
from nodeclass.storage.factory import Factory as StorageFactory
from nodeclass.storage.uri import Uri
from nodeclass.utils.url import FileUrl
from nodeclass.value.hierarchy import Hierarchy

directory = os.path.dirname(os.path.realpath(__file__))

uri_single = 'yaml_fs:{0}'.format(os.path.join(directory, 'data/001'))

uri_simple = {
    'classes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/001/classes')),
    'nodes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/001/nodes'))
}

uri_full = {
    'classes': {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/001/classes'),
    },
    'nodes': {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/001/nodes'),
    },
}

uri_override = {
    'classes': {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/002/env/prod/classes'),
        'env_overrides': [
            {
                'test': {
                    'resource': 'yaml_fs',
                    'path': os.path.join(directory, 'data/002/env/test/classes'),
                },
            },
        ],
    },
    'nodes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/002/nodes')),
}

uri_list_nodes = [ (uri_single, '001'), (uri_simple, '001'), (uri_full, '001'), (uri_override, '002') ]
uri_list_classes = [ (uri_single, '001'), (uri_simple, '001'), (uri_full, '001'), (uri_override, '002/env/test') ]

class_one = {
    'classes': [ 'two', 'three' ],
    'applications': [ 'B', 'A' ],
    'exports': {
        'two': {
            'a': 22,
            'b': '33',
        },
    },
    'parameters': {
        'alpha': 'A',
        'beta': 1,
        'gamma': [ 1, 2 ],
        'delta': { 'a': 1, 'b': 2, 'c': 3 },
        'epsilon': None,
    },
}

node_alpha = {
    'classes': [ 'one' ],
    'applications': [ 'first', 'second' ],
    'environment': 'test',
    'exports': {
        'one': 12345,
    },
    'parameters': {
        'alpha': { 'one': 1, 'two': 2, 'three': 3 },
        'beta': [ 'a', 'b', 'c' ],
        'gamma': None,
        'delta': '111',
        'epsilon': 222,
    },
}

@pytest.mark.parametrize('uri_config, subpath', uri_list_nodes)
def test_node_loader_filesystem_uri(uri_config, subpath):
    uri = Uri(uri_config, 'test')
    _, node_loader = StorageFactory.loaders(uri)
    proto = node_loader['alpha']
    exports = Hierarchy.from_dict(node_alpha['exports'], proto.url, 'exports')
    parameters = Hierarchy.from_dict(node_alpha['parameters'], proto.url, 'parameters')
    assert(proto.name == 'alpha')
    assert(proto.environment == node_alpha['environment'])
    assert(proto.url.resource == 'yaml_fs')
    assert(proto.url.path == os.path.join(directory, 'data', subpath, 'nodes/alpha.yml'))
    assert(proto.klass.classes == node_alpha['classes'])
    assert(proto.klass.applications == node_alpha['applications'])
    assert(proto.klass.exports == exports)
    assert(proto.klass.parameters == parameters)

@pytest.mark.parametrize('uri_config, subpath', uri_list_classes)
def test_klass_loader_filesystem_uri(uri_config, subpath):
    uri = Uri(uri_config, 'test')
    klass_loader, _ = StorageFactory.loaders(uri)
    klass = klass_loader[('one', 'test')]
    url = FileUrl('one', 'yaml_fs', os.path.join(directory, 'data', subpath, 'classes/one.yml'))
    exports = Hierarchy.from_dict(class_one['exports'], url, 'exports')
    parameters = Hierarchy.from_dict(class_one['parameters'], url, 'parameters')
    assert(klass.name == 'one')
    assert(klass.url == url)
    assert(klass.classes == ['two', 'three'])
    assert(klass.applications == ['B', 'A'])
    assert(klass.exports == exports)
    assert(klass.parameters == parameters)
