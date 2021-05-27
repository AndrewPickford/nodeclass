import os
from reclass.storage.filesystem import FileSystemClasses, FileSystemNodes
from reclass.storage.yaml import Yaml

directory = os.path.dirname(os.path.realpath(__file__))

uri_1 = { 'classes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/classes')),
          'nodes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/nodes')) }

uri_2 = { 'classes': {
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

def test_filesystem_classes_string_uri():
    classes = FileSystemClasses(uri=uri_1['classes'], format=Yaml)
    class_dict, url = classes.get('one', None)
    assert (class_dict == class_one)

def test_filesystem_classes_dict_uri():
    classes = FileSystemClasses(uri=uri_2['classes'], format=Yaml)
    class_dict, url = classes.get('one', None)
    assert (class_dict == class_one)

def test_filesystem_nodes_string_uri():
    nodes = FileSystemNodes(uri=uri_1['nodes'], format=Yaml)
    node_dict, url = nodes.get('alpha')
    assert (node_dict == node_alpha)

def test_filesystem_nodes_dict_uri():
    nodes = FileSystemNodes(uri=uri_2['nodes'], format=Yaml)
    node_dict, url = nodes.get('alpha')
    assert (node_dict == node_alpha)
