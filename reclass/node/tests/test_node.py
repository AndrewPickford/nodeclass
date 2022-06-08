from reclass.context import reclass_context
from reclass.node.klass import Klass
from reclass.node.node import Node
from reclass.node.protonode import ProtoNode
from reclass.settings import Settings
from reclass.value.hierarchy import Hierarchy

reclass_context(Settings())

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
    '_reclass_': {
        'environment': 'test',
        'name': {
            'full': 'one',
            'short': 'one',
        }
    }
}


def test_node_automatic_parameters_true():
    with reclass_context(Settings({'automatic_parameters': True})):
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
    with reclass_context(Settings({'automatic_parameters': False})):
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
