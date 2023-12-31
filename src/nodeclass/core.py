from .context import CONTEXT
from .exceptions import ProcessError
from .interpolator.interpolator import Interpolator
from .node.node import Node
from .storage.factory import Factory as StorageFactory
from .utils.path import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Tuple
    from .interpolator.interpolatednode import InterpolatedNode
    from .storage.loader import KlassLoader, NodeLoader
    from .storage.uri import Uri


def nodeinfo_inner(nodename: 'str', interpolator: 'Interpolator', klass_loader: 'KlassLoader', node_loader: 'NodeLoader') -> 'InterpolatedNode':
    try:
        proto_node = node_loader.primary(nodename, env_override=CONTEXT.settings.env_override)
        node = Node(proto_node, klass_loader)
        return interpolator.interpolate(node, node_loader, klass_loader)
    except ProcessError as exception:
        exception.node = nodename
        raise


def nodeinfo(nodename: 'str', uri: 'Uri') -> 'InterpolatedNode':
    # The klass/node loaders abstract the source of the data
    klass_loader, node_loader = StorageFactory.loaders(uri)
    interpolator = Interpolator()
    return nodeinfo_inner(nodename, interpolator, klass_loader, node_loader)


def nodeinfo_all(uri: 'Uri') -> 'Tuple[List[InterpolatedNode], List[ProcessError]]':
    ''' Return a list of the nodeinfo data of all nodes
    '''
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


def node(nodename: 'str', uri: 'Uri') -> 'Node':
    ''' Return the Node object of the named node without interpolation, which contains
        the list of classes loaded and applications.
        This is primarily to generate the salt top data for a node.
    '''
    klass_loader, node_loader = StorageFactory.loaders(uri)
    try:
        proto_node = node_loader.primary(nodename, env_override=CONTEXT.settings.env_override)
        node = Node(proto_node, klass_loader)
        return node
    except ProcessError as exception:
        exception.node = nodename
        raise


def parameter_analysis(parameter: 'str', nodename: 'str', uri: 'Uri'):
    klass_loader, node_loader = StorageFactory.loaders(uri)
    interpolator = Interpolator()
    parameter_path = Path.fromstring(parameter)
    try:
        proto_node = node_loader.primary(nodename, env_override=CONTEXT.settings.env_override)
        node = Node(proto_node, klass_loader)
        analysis = interpolator.parameter_analysis(parameter_path, node, node_loader, klass_loader)
        return analysis
    except ProcessError as exception:
        exception.node = nodename
        raise
