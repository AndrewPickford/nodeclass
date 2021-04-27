#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from .dictionary import Dictionary
from .list import List
from .merged import Merged
from .plain import Plain

class ValueFactory:
    def __init__(self, settings, parser, scalar):
        self.parser = parser
        self.Scalar = scalar
        self.Merged = type('CustomMerged', (Merged, ), { 'settings': settings })
        self.Plain = type('CustomPlain', (Plain, ), { 'settings': settings, 'Merged': self.Merged })
        self.Dictionary = type('CustomDictionary', (Dictionary, ), { 'settings': settings, 'Merged': self.Merged })
        self.List = type('CustomList', (List, ), { 'settings': settings, 'Merged': self.Merged })

    def make_value_dictionary(self, dictionary, url):
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

        return process_dictionary(dictionary, url)
