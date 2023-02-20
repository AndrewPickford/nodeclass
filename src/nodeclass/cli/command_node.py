import contextlib
import sys
import yaml
import nodeclass.core as core
from ..context import nodeclass_set_context
from ..storage.exceptions import InvalidUri
from .config import process_config_file_and_args

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import argparse
    from typing import TextIO
    from ..storage.uri import Uri


def info(nodename: 'str', output: 'TextIO', uri: 'Uri'):
    nodeinfo = core.nodeinfo(nodename, uri)
    yaml.dump(nodeinfo.as_dict(), output, default_flow_style=False, Dumper=yaml.CSafeDumper)

def apps(nodename: 'str', output: 'TextIO', uri: 'Uri'):
    node = core.node(nodename, uri)
    print('applications:', file=output)
    yaml.dump(node.applications, output, default_flow_style=False, Dumper=yaml.CSafeDumper)

def command_node(args: 'argparse.Namespace'):
    settings, uri = process_config_file_and_args(args)
    nodeclass_set_context(settings)
    with contextlib.ExitStack() as stack:
        output = stack.enter_context(open(args.output, 'w')) if args.output else sys.stdout
        try:
            if args.apps:
                apps(args.node, output, uri)
            else:
                info(args.node, output, uri)
        except InvalidUri as exception:
            exception.location = uri.location
            raise
