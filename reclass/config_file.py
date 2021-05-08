import logging
import os
import yaml
from .constants import CONFIG_FILE_NAME, CONFIG_FILE_SEARCH_PATH

SafeLoader = yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader

def load_config_file(filename = None, search_path = None):
    filename = filename or CONFIG_FILE_NAME
    search_path = search_path or CONFIG_FILE_SEARCH_PATH

    for dir in search_path:
        filepath = os.path.join(dir, filename)
        if os.path.exists(filepath):
            with open(filepath) as file:
                logging.debug('Using config file {0}'.format(filepath))
                return yaml.load(file, Loader=cls.SafeLoader)
        logging.debug('No config file found')
    return {}
