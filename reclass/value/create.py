#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#

from .dictionary import Dictionary
from .list import List
from .plain import Plain

def value(input, uri):
    if isinstance(input, dict):
        return Dictionary(input, uri, value)
    elif isinstance(input, list):
        return List(input, uri, value)
    else:
        return Plain(input, uri)
