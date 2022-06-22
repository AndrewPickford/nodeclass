import collections
import sys
import yaml
import nodeclass.core as core
from ..config_file import load_config_file
from ..context import nodeclass_set_context
from ..exceptions import MultipleNodeErrors, NodeclassError, UnknownConfigSetting
from ..settings import Settings
from ..storage.exceptions import InvalidUri
from .arguments import make_argparser, process_args
from .exceptions import NoInventoryUri

URI = collections.namedtuple('URI', ['config', 'location'], rename=False)

def process_config_file_and_args(args):
    settings_file, uri_file, filename = load_config_file()
    settings_args, uri_args = process_args(args)
    try:
        settings = Settings(collections.ChainMap(settings_args, settings_file))
    except UnknownConfigSetting as exception:
        if exception.name in settings_file:
            exception.location = filename
        elif exception.name in settings_args:
            exception.location = 'command line arguments'
        raise
    if uri_args:
        uri = URI(uri_args, 'commandline arguments')
    elif uri_file:
        uri = URI(uri_file, filename)
    else:
        raise NoInventoryUri()
    return settings, uri


def single_nodeinfo(nodename, uri):
    nodeinfo = core.nodeinfo(nodename, uri.config)
    yaml.dump(nodeinfo.as_dict(), sys.stdout, default_flow_style=False, Dumper=yaml.CSafeDumper)

def single_nodeapps(nodename, uri):
    node = core.node(nodename, uri.config)
    print('applications:')
    yaml.dump(node.applications, sys.stdout, default_flow_style=False, Dumper=yaml.CSafeDumper)

def write_all_nodeinfos(uri, directory):
    nodeinfos, exceptions = core.nodeinfo_all(uri.config)
    for nodeinfo in nodeinfos:
        filename = '{0}/{1}.yml'.format(directory, nodeinfo.name)
        with open(filename, 'w') as file:
            yaml.dump(nodeinfo.as_dict(), file, default_flow_style=False, Dumper=yaml.CSafeDumper)
    if len(exceptions) > 0:
        raise MultipleNodeErrors(exceptions)


def main():
    parser = make_argparser()
    args = parser.parse_args()
    try:
        settings, uri = process_config_file_and_args(args)
        nodeclass_set_context(settings)
        try:
            if args.nodeinfo:
                single_nodeinfo(args.nodeinfo, uri)
            elif args.nodeapps:
                single_nodeapps(args.nodeapps, uri)
            elif args.writeall:
                write_all_nodeinfos(uri, args.writeall)
        except InvalidUri as exception:
            exception.location = uri.location
            raise
    except NodeclassError as exception:
        print(exception)
        sys.exit(1)
