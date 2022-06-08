#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from .exceptions import UnknownConfigSetting

class Settings:
    default_settings = {
        'allow_none_overwrite': True,
        'automatic_parameters': True,
        'delimiter': ':',
        'escape_character': '\\',
        'immutable_prefix': '=',
        'inventory_query_sentinels': ('$[', ']'),
        'overwrite_prefix': '~',
        'reference_sentinels': ('${', '}')
    }

    def __init__(self, settings = None):
        settings = settings or {}
        self.allowed = set(self.default_settings)
        self.update(self.default_settings)
        self.update(settings)

    def __str__(self):
        return str({ name: getattr(self, name) for name in self.default_settings })

    def update(self, settings):
        for name, value in settings.items():
            if name in self.allowed:
                setattr(self, name, value)
            else:
                raise UnknownConfigSetting(name)
