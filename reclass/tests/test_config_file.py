import os
import pytest
from reclass.config_file import load_config_file
from reclass.exceptions import NoConfigFile

directory = os.path.dirname(os.path.realpath(__file__))

uri_expected = { 'classes': {
            'resource': 'yaml_fs',
            'path': 'data/classes'
        },
        'nodes': {
            'resource': 'yaml_fs',
            'path': 'data/nodes'
        }
      }

def test_load_config_file():
    settings, uri = load_config_file(search_path = [ directory ])
    assert(settings == {})
    assert(uri == uri_expected)


def test_load_config_file_no_config_file():
    with pytest.raises(NoConfigFile):
        settings, uri = load_config_file(filename = 'missing.yml', search_path = [ directory ])
    with pytest.raises(NoConfigFile):
        # test config file will not be in the default search path
        settings, uri = load_config_file()