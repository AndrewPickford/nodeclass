import os
import yaml
from .exceptions import YamlParsingError
from .format import Format

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, List, TextIO, Union

class Yaml(Format):

    SafeLoader = yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader
    extensions = ('yml', 'yaml')

    name = 'yaml'

    @classmethod
    def mangle_name(cls, file_name: 'str') -> 'Union[str, None]':
        ''' Return class/node name from file name

            If file name extension is in the extensions list then return the file
            name with the extension stripped. Otherwise return None as file is not
            a class/node file.
        '''
        name, extension = os.path.splitext(file_name)
        if extension[1:] in cls.extensions:
            return name
        return None

    @classmethod
    def possible_class_paths(cls, base: 'str') -> 'List[str]':
        basepaths = [ '{0}'.format(base), '{0}/init'.format(base) ]
        return [ '{0}.{1}'.format(path, ext) for ext in cls.extensions for path in basepaths ]

    @classmethod
    def load(cls, file_pointer: 'TextIO') -> 'Dict':
        ''' Return the yaml data in the file pointer

            In the case of an empty file the yaml.load method returns None, so
            as a special case return an empty dictionary
        '''
        try:
            data = yaml.load(file_pointer, Loader=cls.SafeLoader)
        except Exception as exception:
            raise YamlParsingError(exception)
        if data == None:
            return {}
        return data

    @classmethod
    def process(cls, string: 'str') -> 'Dict':
        try:
            data = yaml.load(string, Loader=cls.SafeLoader)
        except Exception as exception:
            raise YamlParsingError(exception)
        if data == None:
            return {}
        return data
