import logging
import os
import yaml
from .constants import CONFIG_FILE_NAME, CONFIG_FILE_SEARCH_PATH
from .exceptions import ConfigFileParseError, NoConfigFile

SafeLoader = yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader

def split_settings_location(config):
    settings = { key: value for key, value in config.items() if key != 'uri' }
    uri = config.get('uri', None)
    return settings, uri

def load_config_file(filename = None, search_path = None):
    filename = filename or CONFIG_FILE_NAME
    search_path = search_path or CONFIG_FILE_SEARCH_PATH

    for dir in search_path:
        filepath = os.path.join(dir, filename)
        if os.path.exists(filepath):
            logging.debug('Using config file {0}'.format(filepath))
            try:
                with open(filepath) as file:
                    config = yaml.load(file, Loader=SafeLoader)
            except Exception as exception:
                raise ConfigFileParseError(filepath, exception)
            settings, uri = split_settings_location(config)
            return settings, uri, filepath
    raise NoConfigFile(filename, search_path)
