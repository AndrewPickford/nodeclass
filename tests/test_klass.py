#!/usr/bin/python3

import sys
import yaml

from reclass.interpolator import Interpolators
from reclass.node.klass import Klass
from reclass.settings import defaults

if sys.version_info[0] < 3:
    print('python 3 only')
    sys.exit(1)

interpolator = Interpolators.Full(defaults)
inventory = {}

one = Klass(classname='', class_dict={'parameters': {'one': '${three:a}', 'two': {'a': 1, 'b': 2}, 'three': '${two}'}}, url='')
klasses = [ one ]

interpolator.merge_parameters(klasses)
result = interpolator.interpolate_parameters()
print(yaml.dump(result, default_flow_style=False))