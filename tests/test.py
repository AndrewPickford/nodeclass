#!/usr/bin/python3

import sys
import yaml

from storage import InevntoryUri, Storage
from reclass.interpolator import Interpolators

if sys.version_info[0] < 3:
    print('python 3 only')
    sys.exit(1)

inventory_uri = InventoryUri(inventory_uri='file:/home/andrewp/software/src/reclass-refactor/testdata')

inventory_uri = InventoryUri(storage='file', path='/home/andrewp/software/src/reclass-refactor/testdata')

inventory_uri = InventoryUri(classes_uri = 'file:/home/andrewp/software/src/reclass-refactor/testdata/classes',
                             nodes_uri = 'file:/home/andrewp/software/src/reclass-refactor/testdata/nodes')

inventory_uri = InventoryUri(classes_uri = { 'storage': 'file', 'path': 'file:/home/andrewp/software/src/reclass-refactor/testdata/classes' },
                             nodes_uri = { 'storage': 'file', 'path': 'file:/home/andrewp/software/src/reclass-refactor/testdata/nodes' })


nodes_uri:
  storage_type: yaml_fs
  uri: /home/andrewp/reclass/test33/nodes
classes_uri:
  storage_type: yaml_fs
  uri: /home/andrewp/reclass/test33/classes.prod
  env_overrides:
  - dev:
      storage_type: yaml_fs
      uri: /home/andrewp/reclass/test33/classes.dev



storage = Storage(inventory_uri)

one = loader.klass('one')
two = loader.klass('two')
three = loader.klass('three')

interpolator = Interpolators.Full()
inventory = {}
klasses = [ one, two, three ]

result = interpolator.interpolate(klasses, inventory)
print(yaml.dump(result, default_flow_style=False))
