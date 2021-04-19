#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
import re


class Settings:

    known_opts = {
        'delimiter': ':',
        'escape_character': '\\',
        'immutable_prefix': '=',
        'inv_query_sentinels': ('$[', ']'),
        'overwrite_prefix': '~',
        'reference_sentinels': ('${', '}')
    }

    def __init__(self, options={}):
        for opt_name, opt_value in self.known_opts.items():
            setattr(self, opt_name, options.get(opt_name, opt_value))
        self.path_split = r'(?<!\\)' + re.escape(self.delimiter)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return all(getattr(self, opt) == getattr(other, opt) for opt in self.known_opts)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        return self.__copy__()

SETTINGS = Settings()
