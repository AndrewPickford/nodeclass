import distro
import platform
from setuptools import setup, find_packages
from nodeclass.version import DESCRIPTION, VERSION

el7 = {
    'requires': [
        'python36-pyparsing',
    ],
}

el8 = {
    'requires': [
        'python3-pyparsing',
    ],
}

options = { 'bdist_rpm': {} }
if platform.system() == 'Linux':
    if distro.id() == 'rhel' or 'rhel' in distro.like().split():
        if distro.major_version == '7':
            options['bdist_rpm']['requires'] = el7['requires']
        else:
            options['bdist_rpm']['requires'] = el8['requires']

setup(
      packages=find_packages(exclude=['tests']),
      description = DESCRIPTION,
      version = VERSION,
      data_files = [
          ('/etc/nodeclass', []),
          ('/usr/share/nodeclass/salt/modules/pillar', ['external/salt/modules/pillar/nodeclass.py']),
          ('/usr/share/nodeclass/salt/modules/tops', ['external/salt/modules/tops/nodeclass.py']),
      ]
     )
