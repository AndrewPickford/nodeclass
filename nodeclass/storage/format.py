from abc import ABC, abstractmethod

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, List, TextIO, Union


class Format(ABC):

    @property
    @abstractmethod
    def extensions(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @classmethod
    @abstractmethod
    def mangle_name(cls, file_name: 'str') -> 'Union[str, None]':
        ''' Return class/node name from file name

            If file name extension is in the extensions list then return the file
            name with the extension stripped. Otherwise return None as file is not
            a class/node file.
        '''
        pass

    @classmethod
    @abstractmethod
    def possible_class_paths(cls, base: 'str') -> 'List[str]':
        pass

    @classmethod
    @abstractmethod
    def load(cls, file_pointer: 'TextIO') -> 'Dict':
        ''' load data, return dictionary
        '''
        pass

    @classmethod
    @abstractmethod
    def process(cls, string: 'str') -> 'Dict':
        ''' process input string and return dictionary of data
        '''
        pass
