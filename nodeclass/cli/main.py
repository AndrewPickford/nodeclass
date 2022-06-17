import sys
import yaml
import nodeclass.core as core
from collections import ChainMap
from ..config_file import load_config_file
from ..context import nodeclass_set_context
from ..exceptions import MultipleNodeclassErrors, NodeclassError
from ..settings import Settings
from .arguments import make_argparser, process_args
from .exceptions import NoInventoryUri


def process_config_file_and_args(args):
    settings_file, uri_file = load_config_file()
    settings_args, uri_args = process_args(args)
    settings = Settings(ChainMap(settings_args, settings_file))
    if uri_args:
        uri = uri_args
    elif uri_file:
        uri = uri_file
    else:
        raise NoInventoryUri()
    return settings, uri


def single_nodeinfo(nodename, uri):
    nodeinfo = core.nodeinfo(nodename, uri)
    yaml.dump(nodeinfo.as_dict(), sys.stdout, default_flow_style=False, Dumper=yaml.CSafeDumper)

def single_nodeapps(nodename, uri):
    node = core.node(nodename, uri)
    print('applications:')
    yaml.dump(node.applications, sys.stdout, default_flow_style=False, Dumper=yaml.CSafeDumper)

def write_all_nodeinfos(uri, directory):
    nodeinfos, exceptions = core.nodeinfo_all(uri)
    for nodeinfo in nodeinfos:
        filename = '{0}/{1}.yml'.format(directory, nodeinfo.name)
        with open(filename, 'w') as file:
            yaml.dump(nodeinfo.as_dict(), file, default_flow_style=False, Dumper=yaml.CSafeDumper)
    if len(exceptions) > 0:
        raise MultipleNodeclassErrors(exceptions)


def main():
    parser = make_argparser()
    args = parser.parse_args()
    try:
        settings, uri = process_config_file_and_args(args)
        nodeclass_set_context(settings)
        if args.nodeinfo:
            single_nodeinfo(args.nodeinfo, uri)
        elif args.nodeapps:
            single_nodeapps(args.nodeapps, uri)
        elif args.writeall:
            write_all_nodeinfos(uri, args.writeall)
    except NodeclassError as exception:
        print(exception)
        sys.exit(1)
