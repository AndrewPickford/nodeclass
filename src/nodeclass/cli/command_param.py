import contextlib
import sys
import nodeclass.core as core
from ..context import nodeclass_set_context
from ..storage.exceptions import InvalidUri
from .config import process_config_file_and_args

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import argparse
    from typing import TextIO
    from ..storage.uri import Uri


def parameter_analysis(parameter: 'str', nodename: 'str', output: 'TextIO', uri: 'Uri'):
    analysis = core.parameter_analysis(parameter, nodename, uri)
    analysis.print_report()

def command_param(args: 'argparse.Namespace'):
    settings, uri = process_config_file_and_args(args)
    nodeclass_set_context(settings)
    with contextlib.ExitStack() as stack:
        output = stack.enter_context(open(args.output, 'w')) if args.output else sys.stdout
        try:
            parameter_analysis(args.param, args.node, output, uri)
        except InvalidUri as exception:
            exception.location = uri.location
            raise
