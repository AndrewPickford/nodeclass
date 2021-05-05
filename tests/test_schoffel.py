#!/usr/bin/python3

import yaml
from pprint import pprint
from reclass.controller import Controller
from reclass.node.node import Node
from reclass.settings import defaults

controller = Controller(defaults)
node_loader = controller.storage_factory.node_loader('yaml_fs:nodes')
klass_loader = controller.storage_factory.klass_loader('yaml_fs:classes')

nodename = 'schoffel.nikhef.nl'
proto_node = node_loader[nodename]
node = Node(proto_node, klass_loader)

interpolator = controller.interpolator
result = interpolator.interpolate(node, node_loader, klass_loader)
print(yaml.dump(result.as_dict(), default_flow_style=False, Dumper=yaml.CSafeDumper))
