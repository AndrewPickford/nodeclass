from .context import CONTEXT
from .exceptions import ProcessError
from .interpolator.interpolator import Interpolator
from .node.node import Node
from .storage.factory import Factory as StorageFactory


def nodeinfo_inner(nodename, interpolator, klass_loader, node_loader):
    try:
        proto_node = node_loader.primary(nodename, env_override=CONTEXT.settings.env_override)
        node = Node(proto_node, klass_loader)
        return interpolator.interpolate(node, node_loader, klass_loader)
    except ProcessError as exception:
        exception.node = nodename
        raise


def nodeinfo(nodename, uri):
    klass_loader, node_loader = StorageFactory.loaders(uri)
    interpolator = Interpolator()
    return nodeinfo_inner(nodename, interpolator, klass_loader, node_loader)


def nodeinfo_all(uri):
    exceptions = []
    nodeinfos = []
    klass_loader, node_loader = StorageFactory.loaders(uri)
    interpolator = Interpolator()
    for nodename in node_loader.nodenames():
        try:
            nodeinfos.append(nodeinfo_inner(nodename, interpolator, klass_loader, node_loader))
        except ProcessError as exception:
            exceptions.append(exception)
    return nodeinfos, exceptions


def node(nodename, uri):
    klass_loader, node_loader = StorageFactory.loaders(uri)
    try:
        proto_node = node_loader.primary(nodename, env_override=CONTEXT.settings.env_override)
        node = Node(proto_node, klass_loader)
        return node
    except ProcessError as exception:
        exception.node = nodename
        raise
