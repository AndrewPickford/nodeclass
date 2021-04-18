#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#


class ParseError(Exception):

    def __init__(self, input, location):
        super().__init__()
        self.input = input
        self.location = location

    def __str__(self):
        return 'Parse error at position {0} with input: {1}'.format(self.location, self.input)
