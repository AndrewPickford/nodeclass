#!/usr/bin/python3

import yaml
from pprint import pprint
from reclass.interpolator.interpolator import Interpolator
from reclass.node.node import Node
from reclass.settings import defaults
from reclass.storage.factory import Factory as StorageFactory

klasses = StorageFactory.klasses('yaml_fs:classes')
nodes = StorageFactory.nodes('yaml_fs:nodes')

interpolator = Interpolator(defaults)

nodename = 'schoffel.nikhef.nl'
protonode = nodes[nodename]
node = Node(protonode.name, protonode.environment, protonode.klass, klasses)

result = interpolator.interpolate(node, nodes, klasses)
print(yaml.dump(result.parameters.render_all(), default_flow_style=False, Dumper=yaml.CSafeDumper))
