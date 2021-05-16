from .interpolator.interpolator import Interpolator
from .node.node import Node

def nodeinfo(node_name, klass_loader, node_loader):
    proto_node = node_loader[node_name]
    node = Node(proto_node, klass_loader)
    interpolator = Interpolator()
    return interpolator.interpolate(node, node_loader, klass_loader)
