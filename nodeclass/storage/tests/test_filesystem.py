import os
import pytest
from nodeclass.storage.exceptions import NodeNotFound
from nodeclass.storage.filesystem import FileSystemClasses, FileSystemNodes
from nodeclass.storage.uri import Uri
from nodeclass.storage.yaml import Yaml

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

uri_list = [ uri_single, uri_simple, uri_full ]

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

@pytest.mark.parametrize('uri_config', uri_list)
def test_filesystem_classes_uri(uri_config):
    uri = Uri(uri_config, 'test')
    classes = FileSystemClasses(classes_uri=uri.classes_uri, format=Yaml)
    class_dict, url = classes.get('one', None)
    assert (class_dict == class_one)

@pytest.mark.parametrize('uri_config', uri_list)
def test_filesystem_nodes_uri(uri_config):
    uri = Uri(uri_config, 'test')
    nodes = FileSystemNodes(nodes_uri=uri.nodes_uri, format=Yaml)
    node_dict, url = nodes.get('alpha')
    assert (node_dict == node_alpha)

def test_filesystem_nodes_no_such_node():
    uri = Uri(uri_simple, 'test')
    nodes = FileSystemNodes(nodes_uri=uri.nodes_uri, format=Yaml)
    with pytest.raises(NodeNotFound) as info:
        node_dict, url = nodes.get('zeta')
    assert(info.value.node == 'zeta')
    assert(info.value.storage == 'yaml_fs:{0}'.format(os.path.join(directory, 'data/001/nodes')))
