#!/usr/bin/python3

import sys
import yaml

from reclass import Interpolators, Klass

_SafeLoader = yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader

if sys.version_info[0] < 3:
    print('python 3 only')
    sys.exit(1)

with open('one.yml') as f:
    one = yaml.load(f, Loader=_SafeLoader)
with open('two.yml') as f:
    two = yaml.load(f, Loader=_SafeLoader)
with open('three.yml') as f:
    three = yaml.load(f, Loader=_SafeLoader)

interpolator = Interpolators.Full()
inventory = {}
klasses = [ Klass(one, 'one.yml'), Klass(two, 'two.yml'), Klass(three, 'three.yml') ]

result = interpolator.interpolate(klasses, inventory)
print(yaml.dump(result, default_flow_style=False))
