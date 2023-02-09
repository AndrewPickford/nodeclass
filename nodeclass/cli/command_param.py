import contextlib
import sys
import nodeclass.core as core
from ..context import nodeclass_set_context
from ..storage.exceptions import InvalidUri
from .config import process_config_file_and_args

def parameter_analysis(parameter, nodename, output, uri):
    analysis = core.parameter_analysis(parameter, nodename, uri.config)
    analysis.print_report()

def command_param(args):
    settings, uri = process_config_file_and_args(args)
    nodeclass_set_context(settings)
    with contextlib.ExitStack() as stack:
        output = stack.enter_context(open(args.output, 'w')) if args.output else sys.stdout
        try:
            parameter_analysis(args.param, args.node, output, uri)
        except InvalidUri as exception:
            exception.location = uri.location
            raise
