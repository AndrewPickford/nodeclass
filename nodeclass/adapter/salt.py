import logging

log = logging.getLogger(__name__)


def ext_pillar(minion_id, pillar, salt_data):
    log.warning('nodeclass ext_pillar called, minion={0}'.format(minion_id))
    log.warning('opts\n{0}'.format(salt_data['opts']))
    log.warning('settings\n{0}'.format(salt_data['settings']))
    return {}


def top(minion_id, nodeclass_settings, salt_options):
    log.warning('nodeclass top called, minion={0}'.format(minion_id))
    log.warning('settings\n{0}'.format(salt_data['settings']))
    return {}
