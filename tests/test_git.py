#!/usr/bin/python3

import sys
import yaml
from pprint import pprint

from reclass.storage.gitrepo import GitRepoClasses, GitRepoNodes
from reclass.storage.yaml import Yaml

uri = { 'classes': {
            'resource': 'yaml_git',
            'repo': 'git+ssh://git@ndpfgit.nikhef.nl:salt/nikhef-site.git',
            'branch': '__env__',
            'path': 'classes',
        },
        'nodes': {
            'resource': 'yaml_git',
            'repo': 'git+ssh://git@ndpfgit.nikhef.nl:salt/nikhef-nodes.git',
            'branch': 'master',
        },
      }
classes = GitRepoClasses(uri=uri['classes'], format=Yaml)
class_dict, class_url = classes.get('cluster', 'master')
print(class_url)
pprint(class_dict)
print('\n')

nodes = GitRepoNodes(uri=uri['nodes'], format=Yaml)
node_dict, node_url = nodes.get('wn-taai-001.farm.nikhef.nl')
print(node_url)
pprint(node_dict)
