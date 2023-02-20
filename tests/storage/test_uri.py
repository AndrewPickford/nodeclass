import os
from nodeclass.storage.uri import Uri

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


def test_uri_single():
    uri = Uri(uri_single, 'test')
    classes_uri = {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/001/classes'),
    }
    nodes_uri = {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/001/nodes'),
    }
    assert(uri.classes_uri == classes_uri)
    assert(uri.nodes_uri == nodes_uri)
    assert(uri.location == 'test')

def test_uri_simple():
    uri = Uri(uri_simple, 'test')
    classes_uri = {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/001/classes'),
    }
    nodes_uri = {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/001/nodes'),
    }
    assert(uri.classes_uri == classes_uri)
    assert(uri.nodes_uri == nodes_uri)
    assert(uri.location == 'test')


def test_uri_full():
    uri = Uri(uri_full, 'test')
    classes_uri = {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/001/classes'),
    }
    nodes_uri = {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/001/nodes'),
    }
    assert(uri.classes_uri == classes_uri)
    assert(uri.nodes_uri == nodes_uri)
    assert(uri.location == 'test')

def test_uri_override():
    uri = Uri(uri_override, 'test')
    classes_uri = {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/002/env/prod/classes'),
        'env_overrides': [
            {
                'test': {
                    'resource': 'yaml_fs',
                    'path': os.path.join(directory, 'data/002/env/test/classes'),
                }
            }
        ]
    }
    nodes_uri = {
        'resource': 'yaml_fs',
        'path': os.path.join(directory, 'data/002/nodes'),
    }
    assert(uri.classes_uri == classes_uri)
    assert(uri.nodes_uri == nodes_uri)
    assert(uri.location == 'test')
