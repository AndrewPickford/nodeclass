#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from reclass.item.scalar import Scalar as BaseScalar
from .dictionary import Dictionary as BaseDictionary
from .list import List as BaseList
from .merged import Merged as BaseMerged
from .plain import Plain as BasePlain
from .topdictionary import TopDictionary as BaseTopDictionary

class ValueFactory:
    Dictionary = BaseDictionary
    List = BaseList
    Merged = BaseMerged
    Plain = BasePlain
    Scalar = BaseScalar
    TopDictionary = BaseTopDictionary

    def __init__(self, settings, parser):
        self.parser = parser

    def make_value_dictionary(self, dictionary, url):
        def process_top_dictionary(input, url):
            return self.TopDictionary({ k: process(v, url) for k, v in input.items() }, url)

        def process_dictionary(input, url):
            return self.Dictionary({ k: process(v, url) for k, v in input.items() }, url)

        def process_list(input, url):
            return self.List([ process(v, url) for v in input ], url)

        def process_plain(input, url):
            if isinstance(input, str):
                item = self.parser.parse(input)
            else:
                item = self.Scalar(input)
            return self.Plain(item, url)

        def process(input, url):
            if isinstance(input, dict):
                return process_dictionary(input, url)
            elif isinstance(input, list):
                return process_list(input, url)
            else:
                return process_plain(input, url)

        return process_top_dictionary(dictionary, url)
