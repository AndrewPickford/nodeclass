from nodeclass.context import nodeclass_context
from nodeclass.node.klass import Klass
from nodeclass.node.node import Node
from nodeclass.node.protonode import ProtoNode
from nodeclass.settings import Settings
from nodeclass.utils.path import Path
from nodeclass.value.hierarchy import Hierarchy

nodeclass_context(Settings())

nodes = {
    'one': {
        'classes': [],
        'applications': [],
        'environment': 'test',
        'exports': {},
        'parameters': {},
    }
}

auto_klass_parameters = {
    '_auto_': {
        'environment': 'test',
        'name': {
            'full': 'one',
            'short': 'one',
        }
    }
}


def test_node_automatic_parameters_true():
    with nodeclass_context(Settings({'automatic_parameters': True})):
        klass = Klass.from_class_dict(name='one', class_dict=nodes['one'], url='')
        proto = ProtoNode(name='one', environment=nodes['one']['environment'], klass=klass, url='')
        node = Node(proto, None)
    autoklasses = [ klass for klass in node.all_klasses if klass.name == '__auto__' ]
    assert(len(autoklasses) == 1)
    autoklass = autoklasses[0]
    assert(autoklass.name == '__auto__')
    assert(autoklass.url == '__auto__')
    assert(autoklass.classes == [])
    assert(autoklass.applications == [])
    assert(autoklass.exports == Hierarchy.from_dict({}, None, None))
    assert(autoklass.parameters == Hierarchy.from_dict(auto_klass_parameters, None, None))


def test_node_automatic_parameters_false():
    with nodeclass_context(Settings({'automatic_parameters': False})):
        klass = Klass.from_class_dict(name='one', class_dict=nodes['one'], url='')
        proto = ProtoNode(name='one', environment=nodes['one']['environment'], klass=klass, url='')
        node = Node(proto, None)
    autoklasses = [ klass for klass in node.all_klasses if klass.name == '__auto__' ]
    assert(len(autoklasses) == 1)
    autoklass = autoklasses[0]
    assert(autoklass.name == '__auto__')
    assert(autoklass.url == '__auto__')
    assert(autoklass.classes == [])
    assert(autoklass.applications == [])
    assert(autoklass.exports == Hierarchy.from_dict({}, None, None))
    assert(autoklass.parameters == Hierarchy.from_dict({}, None, None))


def test_node_automatic_parameters_name_change():
    with nodeclass_context(Settings({'automatic_parameters': True, 'automatic_parameters_name': '_new_name_'})):
        klass = Klass.from_class_dict(name='one', class_dict=nodes['one'], url='')
        proto = ProtoNode(name='one', environment=nodes['one']['environment'], klass=klass, url='')
        node = Node(proto, None)
    autoklasses = [ klass for klass in node.all_klasses if klass.name == '__auto__' ]
    assert len(autoklasses) == 1
    autoklass = autoklasses[0]
    assert autoklass.name == '__auto__'
    assert autoklass.url == '__auto__'
    assert Path.fromstring('_new_name_') in autoklass.parameters
