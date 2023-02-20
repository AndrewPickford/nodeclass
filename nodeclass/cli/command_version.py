from ..version import VERSION

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import argparse


def command_version(args: 'argparse.Namespace'):
    print('{0}'.format(VERSION))
