import os
from nodeclass.storage.factory import Factory as StorageFactory
from nodeclass.storage.uri import Uri

directory = os.path.dirname(os.path.realpath(__file__))

uri_config = { 'classes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/001/classes')),
               'nodes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/001/nodes')) }

def test_klass_loader():
    uri = Uri(uri_config, 'test')
    klass_loader = StorageFactory.klass_loader(uri.classes_uri)
    assert(klass_loader[('one', None)].name == 'one')

def test_node_loader():
    uri = Uri(uri_config, 'test')
    node_loader = StorageFactory.node_loader(uri.nodes_uri)
    assert(node_loader['alpha'].name == 'alpha')
    assert(len([ n for n in node_loader.nodes() ]) == 1)
