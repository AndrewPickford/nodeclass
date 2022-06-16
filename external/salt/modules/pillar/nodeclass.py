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
    import nodeclass.adapter.salt as nodeclass_adapter
    HAS_NODECLASS = True
except ImportError:
    pass


def __virtual__():
    if HAS_NODECLASS:
        return __virtualname__
    return False


def ext_pillar(minion_id, pillar, **kwargs):
    salt_data = {
        'opts': __opts__,
        'settings': kwargs
    }
    return nodeclass_adapter.ext_pillar(minion_id, pillar, salt_data)
