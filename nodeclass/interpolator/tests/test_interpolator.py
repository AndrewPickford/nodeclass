import os
from nodeclass.context import nodeclass_context
from nodeclass.interpolator.interpolator import Interpolator
from nodeclass.node.node import Node
from nodeclass.settings import Settings
from nodeclass.storage.factory import Factory as StorageFactory
from nodeclass.value.hierarchy import Hierarchy

nodeclass_context(Settings())
directory = os.path.dirname(os.path.realpath(__file__))

def uri(subpath):
    return { 'classes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data', subpath, 'classes')),
             'nodes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data', subpath, 'nodes')) }

def uri_env(subpath):
    return {
        'classes': {
            'resource': 'yaml_fs',
            'path': os.path.join(directory, 'data', subpath, 'classes', 'prod'),
            'env_overrides': [
                {
                    'dev': {
                        'resource': 'yaml_fs',
                        'path': os.path.join(directory, 'data', subpath, 'classes', 'dev'),
                    },
                },
            ],
        },
        'nodes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data', subpath, 'nodes')),
    }

def test_parameter_merging():
    interpolator = Interpolator()
    klass_loader, node_loader = StorageFactory.loaders(uri('001'))
    proto_node = node_loader.primary('node_1', env_override=None)
    with nodeclass_context(Settings({'automatic_parameters': False})):
        node = Node(proto_node, klass_loader)
    result = interpolator.interpolate(node, node_loader, klass_loader)
    expected = {
        'alpha': 'A',
        'beta': 'bbBB',
        'gamma': [ 11, 21, 22, 31, 91, 92 ],
        'delta': {
            'one': 0,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
        },
    }
    assert result.parameters == expected

def test_env_override_none():
    interpolator = Interpolator()
    klass_loader, node_loader = StorageFactory.loaders(uri_env('002'))
    proto_node = node_loader.primary('node_1', env_override=None)
    with nodeclass_context(Settings({'automatic_parameters': False})):
        node = Node(proto_node, klass_loader)
    result = interpolator.interpolate(node, node_loader, klass_loader)
    expected = {
        'a': 0,
        'b': 2,
    }
    assert result.parameters == expected

def test_env_override_active():
    interpolator = Interpolator()
    klass_loader, node_loader = StorageFactory.loaders(uri_env('002'))
    proto_node = node_loader.primary('node_1', env_override='dev')
    with nodeclass_context(Settings({'automatic_parameters': False})):
        node = Node(proto_node, klass_loader)
    result = interpolator.interpolate(node, node_loader, klass_loader)
    expected = {
        'a': 0,
        'b': 9,
    }
    assert result.parameters == expected

def test_env_override_none_inv_query():
    interpolator = Interpolator()
    klass_loader, node_loader = StorageFactory.loaders(uri_env('003'))
    proto_node = node_loader.primary('node_1', env_override=None)
    with nodeclass_context(Settings({'automatic_parameters': False})):
        node = Node(proto_node, klass_loader)
    result = interpolator.interpolate(node, node_loader, klass_loader)
    expected = {
        'alpha': {
            'node_1': 0,
            'node_2': 0,
            'node_3': 0,
        },
        'beta': {
            'node_1': 1,
            'node_2': 1,
            'node_3': 1,
        },
    }
    print(result.parameters)
    assert result.parameters == expected

def test_env_override_active_inv_query():
    interpolator = Interpolator()
    klass_loader, node_loader = StorageFactory.loaders(uri_env('003'))
    proto_node = node_loader.primary('node_1', env_override='dev')
    with nodeclass_context(Settings({'automatic_parameters': False})):
        node = Node(proto_node, klass_loader)
    result = interpolator.interpolate(node, node_loader, klass_loader)
    expected = {
        'alpha': {
            'node_2': 0,
            'node_3': 0,
        },
        'beta': {
            'node_1': 1,
            'node_2': 1,
            'node_3': 1,
        },
    }
    assert result.parameters == expected
