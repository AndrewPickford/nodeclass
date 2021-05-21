#!/usr/bin/python3

import sys
import yaml
from pprint import pprint

from reclass.storage.factory import Factory as StorageFactory

uri_1 = 'yaml_fs:/home/andrewp/reclass/test35'

uri_2 = { 'classes': 'yaml_fs:/home/andrewp/reclass/test35/classes',
          'nodes': 'yaml_fs:/home/andrewp/reclass/test35/nodes', }

uri_3 = { 'classes': {
            'resource': 'yaml_fs',
            'path': '/home/andrewp/reclass/test35/classes',
        },
        'nodes': {
            'resource': 'yaml_fs',
            'path': '/home/andrewp/reclass/test35/nodes',
        },
      }

klass_loader, node_loader = StorageFactory.loaders(uri_2)
klass = klass_loader[('cluster', None)]
pprint(klass)
print('\n')

proto = node_loader[('wn-taai-001.farm.nikhef.nl')]
pprint(proto)
