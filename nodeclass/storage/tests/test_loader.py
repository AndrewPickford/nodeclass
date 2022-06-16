import os
from nodeclass.storage.factory import Factory as StorageFactory

directory = os.path.dirname(os.path.realpath(__file__))

uri = { 'classes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/classes')),
        'nodes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/nodes')) }

def test_klass_loader():
    klass_loader = StorageFactory.klass_loader(uri['classes'])
    assert(klass_loader[('one', None)].name == 'one')

def test_node_loader():
    node_loader = StorageFactory.node_loader(uri['nodes'])
    assert(node_loader['alpha'].name == 'alpha')
    assert(len([ n for n in node_loader.nodes() ]) == 1)
