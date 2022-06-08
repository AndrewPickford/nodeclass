import pytest
from reclass.exceptions import UnknownConfigSetting
from reclass.settings import Settings

valid = { 'allow_none_overwrite': True,
          'automatic_parameters': True,
          'delimiter': ':',
          'escape_character': '\\',
          'immutable_prefix': '=',
          'inventory_query_sentinels': ('$[', ']'),
          'overwrite_prefix': '~',
          'reference_sentinels': ('${', '}')
        }

invalid = { 'allow_none_overwrite': True,
            'unknown': False
          }


def test_settings_valid():
    settings = Settings(valid)
    assert(settings.allow_none_overwrite == True)
    assert(settings.reference_sentinels == ('${', '}'))

def test_settings_invalid():
    with pytest.raises(UnknownConfigSetting) as info:
        Settings(invalid)
    assert(info.value.name == 'unknown')
