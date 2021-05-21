#!/usr/bin/python3

import sys
import yaml
from pprint import pprint

from reclass.storage.filesystem import FileSystemClasses, FileSystemNodes
from reclass.storage.yaml import Yaml

uri = { 'classes': {
            'resource': 'yaml_fs',
            'path': '/home/andrewp/reclass/test35/classes',
        },
        'nodes': {
            'resource': 'yaml_fs',
            'path': '/home/andrewp/reclass/test35/nodes',
        },
      }
classes = FileSystemClasses(uri=uri['classes'], format=Yaml)
class_dict, class_url = classes.get('cluster', 'master')
print(class_url)
pprint(class_dict)
print('\n')

nodes = FileSystemNodes(uri=uri['nodes'], format=Yaml)
node_dict, node_url = nodes.get('wn-taai-001.farm.nikhef.nl')
print(node_url)
pprint(node_dict)
