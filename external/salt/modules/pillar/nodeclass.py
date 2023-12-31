"""
Nodeclass Pillar Module
=======================

.. code-block:: yaml

"""

import copy
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


def ext_pillar(minion_id, pillar, **kwargs):
    settings = kwargs
    options = {}
    if __opts__.get('saltenv', None):
        options['env_override'] = __opts__['saltenv']
    if __opts__.get('pillarenv', None):
        options['env_override'] = __opts__['pillarenv']
    if len(options) > 0:
        settings = copy.copy(kwargs)
        settings.update(options)
    return nodeclass_adapter.ext_pillar(minion_id, pillar, settings)
