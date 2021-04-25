#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
import re
from .defaults import default_settings
from .exceptions import UnknownSettingError

class Settings:

    def __init__(self, settings):
        self.allowed = set(default_settings)
        self.update(default_settings)
        self.update(settings)

    def update(self, settings):
        for name, value in settings.items():
            if name in self.allowed:
                setattr(self, name, value)
            else:
                raise UnknownSettingError(name)
        self.path_split = r'(?<!\\)' + re.escape(self.delimiter)

defaults = Settings({})
