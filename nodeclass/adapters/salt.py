import logging
import nodeclass.core as core
from ..config_file import split_settings_location
from ..context import nodeclass_set_context
from ..settings import Settings

log = logging.getLogger(__name__)


def ext_pillar(minion_id, pillar, settings, options):
    settings, uri = split_settings_location(settings)
    settings_context = Settings(settings)
    nodeclass_set_context(settings_context)
    nodeinfo = core.nodeinfo(minion_id, uri)
    parameters = nodeinfo.as_dict().get('parameters', {})
    return parameters


def top(minion_id, settings, options):
    settings, uri = split_settings_location(settings)
    settings_context = Settings(settings)
    nodeclass_set_context(settings_context)
    node = core.node(minion_id, uri)
    return { node.environment: node.applications }
