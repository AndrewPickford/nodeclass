#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#

'''
Import Factory class as Value to give a factory pattern for making
value objects:

from reclass.value import Value
value = Value.Create(src_dict, '')
'''
from .factory import Factory as Value
