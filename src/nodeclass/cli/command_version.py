from ..__version__ import __version__

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import argparse


def command_version(args: 'argparse.Namespace'):
    print('{0}'.format(__version__))
