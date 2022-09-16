#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from ..exceptions import ProcessError


class RecursiveClassInclude(ProcessError):
    def __init__(self, classname, first):
        super().__init__()
        self.classname = classname
        self.first = first
        self.second = None

    def message(self):
        return super().message() + \
               [ 'Recursive include of class: {0}, in:'.format(self.classname),
                 2,
                 '{0}'.format(self.second),
                 '{0}'.format(self.first) ]
