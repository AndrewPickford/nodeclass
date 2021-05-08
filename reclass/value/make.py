#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from ..context import CONTEXT
from ..item.scalar import Scalar
from .dictionary import Dictionary
from .list import List
from .merged import Merged
from .plain import Plain
from .topdictionary import TopDictionary

def make_value_dictionary(dictionary, url):
    def process_top_dictionary(input, url):
        return TopDictionary({ k: process(v, url) for k, v in input.items() }, url)

    def process_dictionary(input, url):
        return Dictionary({ k: process(v, url) for k, v in input.items() }, url)

    def process_list(input, url):
        return List([ process(v, url) for v in input ], url)

    def process_plain(input, url):
        if isinstance(input, str):
            item = CONTEXT.item_parser.parse(input)
        else:
            item = Scalar(input)
        return Plain(item, url)

    def process(input, url):
        if isinstance(input, dict):
            return process_dictionary(input, url)
        elif isinstance(input, list):
            return process_list(input, url)
        else:
            return process_plain(input, url)

    return process_top_dictionary(dictionary, url)
