import os
from .version import NAME

CONFIG_FILE_NAME = 'nodeclass-config.yml'

CONFIG_FILE_SEARCH_PATH = [
    os.getcwd(),
    os.path.join(os.path.expanduser('~'), '.nodeclass'),
    os.path.join('/etc', NAME)
]
