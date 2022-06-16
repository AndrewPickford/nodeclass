import os
import pytest
from nodeclass.storage.factory import Factory as StorageFactory
from nodeclass.value.hierarchy import Hierarchy

directory = os.path.dirname(os.path.realpath(__file__))

uri_single = 'yaml_fs:{0}'.format(os.path.join(directory, 'data'))

uri_simple = { 'classes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/classes')),
               'nodes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/nodes')) }

uri_full = { 'classes': {
               'resource': 'yaml_fs',
               'path': os.path.join(directory, 'data/classes'),
             },
             'nodes': {
               'resource': 'yaml_fs',
               'path': os.path.join(directory, 'data/nodes'),
             },
           }

uri_list = [ pytest.param(uri_single, id='single'),
             pytest.param(uri_simple, id='simple'),
             pytest.param(uri_full, id='full') ]

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

@pytest.mark.parametrize('uri', uri_list)
def test_node_loader_filesystem_uri(uri):
    _, node_loader = StorageFactory.loaders(uri)
    proto = node_loader['alpha']
    exports = Hierarchy.from_dict(node_alpha['exports'], proto.url, 'exports')
    parameters = Hierarchy.from_dict(node_alpha['parameters'], proto.url, 'parameters')
    assert(proto.name == 'alpha')
    assert(proto.environment == node_alpha['environment'])
    assert(proto.url == 'yaml_fs:{0}'.format(os.path.join(directory, 'data/nodes/alpha.yml')))
    assert(proto.klass.classes == node_alpha['classes'])
    assert(proto.klass.applications == node_alpha['applications'])
    assert(proto.klass.exports == exports)
    assert(proto.klass.parameters == parameters)

@pytest.mark.parametrize('uri', uri_list)
def test_klass_loader_filesystem_uri(uri):
    klass_loader, _ = StorageFactory.loaders(uri)
    klass = klass_loader[('one', None)]
    url = 'yaml_fs:{0}'.format(os.path.join(directory, 'data/classes/one.yml'))
    exports = Hierarchy.from_dict(class_one['exports'], url, 'exports')
    parameters = Hierarchy.from_dict(class_one['parameters'], url, 'parameters')
    assert(klass.name == 'one')
    assert(klass.url == url)
    assert(klass.classes == ['two', 'three'])
    assert(klass.applications == ['B', 'A'])
    assert(klass.exports == exports)
    assert(klass.parameters == parameters)
