import argparse
from ..version import NAME, DESCRIPTION

CLI_DEFAULT_OPTS = {
    'log_level': 'WARNING',
}

def add_data_location_options(parser):
    group = parser.add_argument_group('Data location options',
        'Location to read data in from. The data location is described in the form of a URI, which '
        'is composed of a resource type and path within the resource, separated by a colon. For example: '
        'yaml_fs:/path/to/data. If the data URI is specified on the command line this overrides any URIs '
        'defined in the configuration file. If given use either --uri or --uri-class and --uri-node')
    group.add_argument('--uri', type=str, metavar='URI', help='URI for both the nodes and classes data')
    group.add_argument('--uri-classes', dest='uri_classes', type=str, metavar='URI', help='classes data URI')
    group.add_argument('--uri-nodes', dest='uri_nodes', type=str, metavar='URI', help='nodes data URI')
    return group

def add_config_file_options(parser):
    group = parser.add_argument_group('Config file options')
    group.add_argument('--config-filename', type=str, help='Config file to use')

def add_output_options(parser):
    group = parser.add_argument_group('Output options')
    group.add_argument('--apps', action='store_true', help='output application list only')
    return group

def add_processing_options(parser):
    group = parser.add_argument_group('Processing options')
    group.add_argument('--environment', type=str, metavar='ENV', help='Override the environment of the node during processing')
    return group

def add_param_output_options(parser):
    group = parser.add_argument_group('Output options')
    group.add_argument('--output', type=str, metavar='PATH', help='write output to file at PATH instead of standard output')
    return group

def add_inventory_sub_parser(sub_parsers):
    parser = sub_parsers.add_parser('inventory', help='output data for all nodes')
    group = add_output_options(parser)
    group.add_argument('--output', type=str, metavar='PATH', default='.', help='write output in directory at PATH')
    add_config_file_options(parser)
    add_data_location_options(parser)
    return

def add_node_sub_parser(sub_parsers):
    parser = sub_parsers.add_parser('node', help='output data for one node')
    parser.add_argument('node', type=str, metavar='NODE', nargs='?', help='node')
    group = add_output_options(parser)
    group.add_argument('--output', type=str, metavar='PATH', help='write output to file at PATH instead of standard output')
    add_config_file_options(parser)
    add_data_location_options(parser)
    add_processing_options(parser)
    return

def add_param_sub_parser(sub_parsers):
    parser = sub_parsers.add_parser('param', help='analyse a parameter for a node')
    add_param_output_options(parser)
    add_config_file_options(parser)
    add_data_location_options(parser)
    add_processing_options(parser)
    parser.add_argument('param', type=str, metavar='PARAM', help='parameter to analyse')
    parser.add_argument('node', type=str, metavar='NODE', help='node to use for parameter analysis')
    return

def add_version_sub_parser(sub_parsers):
    sub_parsers.add_parser('version', help='print version')
    return

def make_parser() -> 'argparse.ArgumentParser':
    parser = argparse.ArgumentParser(prog=NAME, description=DESCRIPTION)
    sub_parsers = parser.add_subparsers(dest='command')
    add_inventory_sub_parser(sub_parsers)
    add_node_sub_parser(sub_parsers)
    add_param_sub_parser(sub_parsers)
    add_version_sub_parser(sub_parsers)
    return parser
