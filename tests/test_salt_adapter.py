import os
from nodeclass.adapters.salt import ext_pillar as salt_pillar_adapter, top as salt_top_adapter
from .node_1 import node_1

directory = os.path.dirname(os.path.realpath(__file__))


config = {
    'uri': {
        'classes': {
            'resource': 'yaml_fs',
            'path': os.path.join(directory, 'data/001/env/prod/classes'),
            'env_overrides': [
                {
                    'dev': {
                        'resource': 'yaml_fs',
                        'path': os.path.join(directory, 'data/001/env/dev/classes'),
                    },
                },
            ],
        },
        'nodes': 'yaml_fs:{0}'.format(os.path.join(directory, 'data/001/nodes')),
    },
}


def test_salt_adapter_top():
    applications = salt_top_adapter('node_1', config)
    result = { 'prod': node_1['applications'] }
    assert(applications == result)

def test_salt_adapter_pillar():
    pillar = salt_pillar_adapter('node_1', {}, config)
    print(pillar)
    assert(pillar == node_1['parameters'])
