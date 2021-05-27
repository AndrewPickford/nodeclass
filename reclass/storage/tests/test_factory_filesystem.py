import os
from reclass.storage.factory import Factory as StorageFactory
from reclass.value.hierarchy import Hierarchy

directory = os.path.dirname(os.path.realpath(__file__))

uri_1 = 'yaml_fs:{0}'.format(os.path.join(directory, 'data'))

uri_2 = { 'classes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/classes')),
          'nodes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/nodes')) }

uri_3 = { 'classes': {
            'resource': 'yaml_fs',
            'path': os.path.join(directory, 'data/classes'),
        },
        'nodes': {
            'resource': 'yaml_fs',
            'path': os.path.join(directory, 'data/nodes'),
        },
      }

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

def test_node_loader_filesystem_single_string_uri():
    _, node_loader = StorageFactory.loaders(uri_1)
    proto = node_loader['alpha']
    exports = Hierarchy.from_dict(node_alpha['exports'], proto.url)
    parameters = Hierarchy.from_dict(node_alpha['parameters'], proto.url)
    assert(proto.name == 'alpha')
    assert(proto.environment == node_alpha['environment'])
    assert(proto.url == 'yaml_fs:{0}'.format(os.path.join(directory, 'data/nodes/alpha.yml')))
    assert(proto.klass.classes == node_alpha['classes'])
    assert(proto.klass.applications == node_alpha['applications'])
    assert(proto.klass.exports == exports)
    assert(proto.klass.parameters == parameters)

def test_klass_loader_filesystem_single_string_uri():
    klass_loader, _ = StorageFactory.loaders(uri_1)
    klass = klass_loader[('one', None)]
    url = 'yaml_fs:{0}'.format(os.path.join(directory, 'data/classes/one.yml'))
    exports = Hierarchy.from_dict(class_one['exports'], url)
    parameters = Hierarchy.from_dict(class_one['parameters'], url)
    assert(klass.name == 'one')
    assert(klass.url == url)
    assert(klass.classes == ['two', 'three'])
    assert(klass.applications == ['B', 'A'])
    assert(klass.exports == exports)
    assert(klass.parameters == parameters)
