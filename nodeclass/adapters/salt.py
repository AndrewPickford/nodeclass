import logging
from ..core import nodeinfo as core_nodeinfo, node as core_node
from ..cli.exceptions import NoInventoryUri
from ..config_file import split_settings_location
from ..context import nodeclass_set_context
from ..exceptions import UnknownConfigSetting
from ..settings import Settings
from ..storage.uri import Uri
from ..version import NAME

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict
    from ..settings import ConfigDict


log = logging.getLogger(__name__)


def ext_pillar(minion_id: 'str', pillar: 'Dict', config: 'ConfigDict') -> 'Dict':
    settings_config, uri_config = split_settings_location(config)
    try:
        settings = Settings(settings_config)
    except UnknownConfigSetting as exception:
        exception.location = 'pillar configuration for {0}'.format(NAME)
        raise
    if uri_config is None:
        raise NoInventoryUri()
    uri = Uri(uri_config, 'salt settings')
    nodeclass_set_context(settings)
    nodeinfo = core_nodeinfo(minion_id, uri)
    parameters = nodeinfo.as_dict().get('parameters', {})
    return parameters


def top(minion_id: 'str', config: 'ConfigDict') -> 'Dict':
    settings_config, uri_config = split_settings_location(config)
    try:
        settings = Settings(settings_config)
    except UnknownConfigSetting as exception:
        exception.location = 'top configuration of {0}'.format(NAME)
        raise
    if uri_config is None:
        raise NoInventoryUri()
    uri = Uri(uri_config, 'salt settings')
    nodeclass_set_context(settings)
    node = core_node(minion_id, uri)
    return { node.environment: node.applications }
