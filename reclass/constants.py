import os
from .version import NAME

CONFIG_FILE_NAME = 'reclass.yml'

CONFIG_FILE_SEARCH_PATH = [
    os.getcwd(),
    os.path.expanduser('~'),
    os.path.join('/etc', NAME)
]
