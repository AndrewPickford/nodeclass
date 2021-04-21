#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from abc import ABC, abstractmethod
from .dictionary import Dictionary
from .list import List
from .plain import Plain

class Factory(ABC):
    @staticmethod
    def Create(input, uri):
        def callback(input, uri):
            if isinstance(input, dict):
                return Dictionary(input, uri, callback)
            elif isinstance(input, list):
                return List(input, uri, callback)
            else:
                return Plain(input, uri)
        return callback(input, uri)

    @abstractmethod
    def NotAllowed(self):
        '''
        Block Factory from instantiating
        '''
        pass

