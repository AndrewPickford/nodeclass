import sys
import yaml
import reclass.core as core
from collections import ChainMap
from ..config_file import load_config_file
from ..context import reclass_set_context
from ..exceptions import ReclassError, ReclassRuntimeError
from ..settings import Settings
from ..storage.factory import Factory as StorageFactory
from .arguments import make_argparser, process_args


def print_with_indent(indent, message):
    for offset, line in message:
        current_indent = indent + offset
        print('  ' * current_indent, line, sep='')


def handle_nodeinfo(node_name, klass_loader, node_loader):
    try:
        nodeinfo = core.nodeinfo(node_name, klass_loader, node_loader)
        print(yaml.dump(nodeinfo.as_dict(), default_flow_style=False, Dumper=yaml.CSafeDumper))
    except ReclassError as exc:
        print('--> {0}'.format(node_name))
        print_with_indent(2, exc.message)
        sys.exit(1)


def process_config_file_and_args(args):
    settings_file, uri_file = load_config_file()
    settings_args, uri_args = process_args(args)
    settings = Settings(ChainMap(settings_args, settings_file))
    if uri_args:
        uri = uri_args
    elif uri_file:
        uri = uri_file
    else:
        ReclassRuntimeError('No location for inventory specified')
    return settings, uri


def main():
    parser = make_argparser()
    args = parser.parse_args()
    try:
        settings, uri = process_config_file_and_args(args)
        reclass_set_context(settings)
        klass_loader, node_loader = StorageFactory.loaders(uri)
    except ReclassError as exc:
        print_with_indent(0, exc.message)
        sys.exit(1)
    if args.nodeinfo:
        handle_nodeinfo(args.nodeinfo, klass_loader, node_loader)
