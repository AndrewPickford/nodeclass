"""
Nodeclass Pillar Module
=======================

.. code-block:: yaml

"""

import logging

log = logging.getLogger(__name__)

__virtualname__ = "nodeclass"

HAS_NODECLASS = False
try:
    import nodeclass.adapters.salt as nodeclass_adapter
    HAS_NODECLASS = True
except ImportError:
    pass


def __virtual__():
    if HAS_NODECLASS:
        return __virtualname__
    return False


def top(**kwargs):
    if "id" not in kwargs["opts"]:
        log.warning("Minion id not found - Returning empty dict")
        return {}
    minion_id = kwargs["opts"]["id"]
    settings = __opts__["master_tops"]["nodeclass"]
    options = {}
    if __opts__.get('saltenv', None):
        options['env_override'] = kwargs['opts']['saltenv']
    if __opts__.get('pillarenv', None):
        options['env_override'] = kwargs['opts']['pillarenv']
    if len(options) > 0:
        settings = copy.copy(__opts__["master_tops"]["nodeclass"])
        settings.update(options)
    return nodeclass_adapter.top(minion_id, settings)
