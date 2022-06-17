from setuptools import setup, find_packages
from nodeclass.version import DESCRIPTION, VERSION

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
