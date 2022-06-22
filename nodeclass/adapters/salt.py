import logging
import nodeclass.core as core
from ..config_file import split_settings_location
from ..context import nodeclass_set_context
from ..exceptions import UnknownConfigSetting
from ..settings import Settings
from ..version import NAME

log = logging.getLogger(__name__)


def ext_pillar(minion_id, pillar, settings):
    settings, uri = split_settings_location(settings)
    try:
        settings_context = Settings(settings)
    except UnknownConfigSetting as exception:
        exception.location = 'pillar configuration for {0}'.format(NAME)
        raise
    nodeclass_set_context(settings_context)
    nodeinfo = core.nodeinfo(minion_id, uri)
    parameters = nodeinfo.as_dict().get('parameters', {})
    return parameters


def top(minion_id, settings):
    settings, uri = split_settings_location(settings)
    try:
        settings_context = Settings(settings)
    except UnknownConfigSetting as exception:
        exception.location = 'top configuration of {0}'.format(NAME)
        raise
    nodeclass_set_context(settings_context)
    node = core.node(minion_id, uri)
    return { node.environment: node.applications }
