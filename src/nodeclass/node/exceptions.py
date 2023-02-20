#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from ..exceptions import ProcessError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional
    from ..exceptions import MessageList
    from ..utils.url import Url

class RecursiveClassInclude(ProcessError):
    def __init__(self, classname: 'str', first: 'Url'):
        super().__init__()
        self.classname = classname
        self.first = first
        self.second: Optional['Url'] = None

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Recursive include of class: {0}, in:'.format(self.classname),
                 2,
                 '{0}'.format(self.second),
                 '{0}'.format(self.first) ]
