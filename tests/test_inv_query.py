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

one = Klass(classname=' ', class_dict={'exports': { 'alpha': 'aaa' }, 'parameters': { 'a': '${b}', 'b': 1, 'c':'$[ exports:alpha ]'}}, url=' ')
klasses = [ one ]

result = interpolator.interpolate(klasses, None, None, None)
print(yaml.dump(result, default_flow_style=False))
