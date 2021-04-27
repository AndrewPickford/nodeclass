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
inventory = {}

nodename = 'wn-taai-001.farm.nikhef.nl'
node_dict, url = nodes[nodename]
node = Node(nodename, node_dict, url, classes)
result = interpolator.interpolate(node.classes, inventory)
print(yaml.dump(result, default_flow_style=False))
