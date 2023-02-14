#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from .exceptions import UnknownConfigSetting

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Tuple

class Settings:
    default_settings = {
        'allow_none_overwrite': True,
        'automatic_parameters': True,
        'automatic_parameters_name': '_auto_',
        'delimiter': ':',
        'escape_character': '\\',
        'env_override': None,
        'immutable_prefix': '=',
        'inventory_query_sentinels': ('$[', ']'),
        'overwrite_prefix': '~',
        'reference_sentinels': ('${', '}')
    }

    def __init__(self, settings: 'Optional[Dict[str, Any]]' = None):
        self.allow_none_overwrite: 'bool'
        self.automatic_parameters: 'bool'
        self.automatic_parameters_name: 'str'
        self.delimiter: 'str'
        self.escape_character: 'str'
        self.env_override: 'Optional[str]'
        self.immutable_prefix: 'str'
        self.inventory_query_sentinels: 'Tuple[str, str]'
        self.overwrite_prefix: 'str'
        self.reference_sentinels: 'Tuple[str, str]'
        settings = settings or {}
        self.allowed = set(self.default_settings)
        self.update(self.default_settings)
        self.update(settings)

    def __str__(self) -> 'str':
        return str({ name: getattr(self, name) for name in self.default_settings })

    def update(self, settings: 'Dict[str, Any]'):
        for name, value in settings.items():
            if name in self.allowed:
                setattr(self, name, value)
            else:
                raise UnknownConfigSetting(name)
