#!/usr/bin/python3

import sys
import yaml

from reclass.value import value

_SafeLoader = yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader

if sys.version_info[0] < 3:
    print('python 3 only')
    sys.exit(1)

with open('one.yml') as f:
    one = yaml.load(f, Loader=_SafeLoader)
with open('two.yml') as f:
    two = yaml.load(f, Loader=_SafeLoader)

a = value(one, 'one.yml')
b = value(two, 'two.yml')
a = a.merge(b)

print(a.render())
