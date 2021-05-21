import os
import yaml

class Yaml:

    SafeLoader = yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader
    extensions = ('yml', 'yaml')

    name = 'yaml'

    @classmethod
    def mangle_name(cls, file_name):
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
    def possible_class_paths(cls, base):
        basepaths = [ '{0}'.format(base), '{0}/init'.format(base) ]
        return [ '{0}.{1}'.format(path, ext) for ext in cls.extensions for path in basepaths ]

    @classmethod
    def load(cls, file_pointer):
        return yaml.load(file_pointer, Loader=cls.SafeLoader)

    @classmethod
    def process(cls, string):
        return yaml.load(string, Loader=cls.SafeLoader)
