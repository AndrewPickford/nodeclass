#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from .dictionary import Dictionary
from .list import List
from .merged import Merged
from .plain import Plain
from .topdictionary import TopDictionary

class ValueFactory:
    def __init__(self, settings, parser):
        self.parser = parser
        self.Scalar = parser.Scalar
        self.Merged = type('XMerged', (Merged, ), { 'settings': settings })
        self.Plain = type('XPlain', (Plain, ), { 'settings': settings, 'Merged': self.Merged })
        self.Dictionary = type('XDictionary', (Dictionary, ),
            { 'settings': settings, 'Merged': self.Merged })
        self.TopDictionary = type('XTopDictionary', (TopDictionary, ),
            { 'settings': settings, 'Merged': self.Merged, 'Dictionary': self.Dictionary })
        self.List = type('XList', (List, ), { 'settings': settings, 'Merged': self.Merged })

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
