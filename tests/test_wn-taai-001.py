#!/usr/bin/python3

import yaml
from pprint import pprint
from reclass.storage.factory import Factory as StorageFactory
from reclass.interpolator.interpolator import Interpolator
from reclass.node.node import Node

node_loader = StorageFactory.node_loader('yaml_fs:nodes')
klass_loader = StorageFactory.klass_loader('yaml_fs:classes')

proto_node = node_loader['wn-taai-001.farm.nikhef.nl']
node = Node(proto_node, klass_loader)

interpolator = Interpolator()
result = interpolator.interpolate(node, node_loader, klass_loader)
print(yaml.dump(result.as_dict(), default_flow_style=False, Dumper=yaml.CSafeDumper))
