import contextlib
import sys
import yaml
import nodeclass.core as core
from ..context import nodeclass_set_context
from ..storage.exceptions import InvalidUri
from .config import process_config_file_and_args

def info(nodename, output, uri):
    nodeinfo = core.nodeinfo(nodename, uri.config)
    yaml.dump(nodeinfo.as_dict(), output, default_flow_style=False, Dumper=yaml.CSafeDumper)

def apps(nodename, output, uri):
    node = core.node(nodename, uri.config)
    print('applications:', file=output)
    yaml.dump(node.applications, output, default_flow_style=False, Dumper=yaml.CSafeDumper)

def command_node(args):
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
