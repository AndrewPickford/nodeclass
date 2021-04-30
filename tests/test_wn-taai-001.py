#!/usr/bin/python3

import yaml
from pprint import pprint
from reclass.interpolator import Interpolators
from reclass.node.node import Node
from reclass.settings import defaults
from reclass.storage.factory import Factory as StorageFactory

classes = StorageFactory.classes('yaml_fs:classes')
nodes = StorageFactory.nodes('yaml_fs:nodes')

interpolator = Interpolators.Full(defaults)
inventory_interpolator = Interpolators.Inventory(defaults)

nodename = 'wn-taai-001.farm.nikhef.nl'
node_dict, url = nodes[nodename]
node = Node(nodename, node_dict, url, classes)

node.interpolate(interpolator, inventory_interpolator, nodes, classes)
print(yaml.dump(node.to_dict(), default_flow_style=False, Dumper=yaml.CSafeDumper))
