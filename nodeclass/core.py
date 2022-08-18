from .context import CONTEXT
from .exceptions import ProcessError
from .interpolator.interpolator import Interpolator
from .node.node import Node
from .storage.factory import Factory as StorageFactory

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Union
    from .interpolator.interpolatednode import InterpolatedNode
    from .storage.loader import KlassLoader, NodeLoader


def nodeinfo_inner(nodename: 'str', interpolator: 'Interpolator', klass_loader: 'KlassLoader', node_loader: 'NodeLoader') -> 'InterpolatedNode':
    try:
        proto_node = node_loader.primary(nodename, env_override=CONTEXT.settings.env_override)
        node = Node(proto_node, klass_loader)
        return interpolator.interpolate(node, node_loader, klass_loader)
    except ProcessError as exception:
        exception.node = nodename
        raise


def nodeinfo(nodename: 'str', uri: 'Union[str, Dict]') -> 'InterpolatedNode':
    # The klass/node loaders abstract the source of the data
    klass_loader, node_loader = StorageFactory.loaders(uri)
    interpolator = Interpolator()
    return nodeinfo_inner(nodename, interpolator, klass_loader, node_loader)


def nodeinfo_all(uri: 'Union[str, Dict]') -> 'Tuple[List[InterpolatedNode], List[ProcessError]]':
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


def node(nodename: 'str', uri: 'Union[str, Dict]') -> 'Node':
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
