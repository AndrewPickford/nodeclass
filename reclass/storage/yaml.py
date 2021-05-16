import yaml

class Yaml:

    SafeLoader = yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader
    extensions = ('yml', 'yaml')

    name = 'yaml'

    @classmethod
    def load(cls, path):
        with open(path) as file:
            return yaml.load(file, Loader=cls.SafeLoader)

    @classmethod
    def process(cls, string):
        return yaml.load(string, Loader=cls.SafeLoader)
