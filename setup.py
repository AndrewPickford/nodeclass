from setuptools import setup, find_packages
from nodeclass.version import DESCRIPTION, VERSION

setup(
      packages=find_packages(exclude=['tests']),
      description = DESCRIPTION,
      version = VERSION,
      data_files = [
          ('/usr/share/nodeclass', ['external/salt/modules/pillar/nodeclass.py']),
          ('/usr/share/nodeclass', ['external/salt/modules/tops/nodeclass.py']),
      ]
     )
