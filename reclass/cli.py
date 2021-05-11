import argparse
from .config_file import load_config_file
from .version import NAME, DESCRIPTION, VERSION

cli_default_opts = {
    'log_level': 'OFF',
}

def add_run_mode_options(parser):
    group = parser.add_argument_group('Run mode',
        'Configure which data {0} outputs. Options are multually exclusive.'.format(parser.prog))
    run_group = group.add_mutually_exclusive_group(required=True)
    run_group.add_argument('--nodeinfo',
        dest = 'nodeinfo',
        type = str,
        metavar = 'NODE',
        help = 'Output the full reclass data for the given node.')
    run_group.add_argument('--nodeapps',
        dest = 'nodeapps',
        type = str,
        metavar = 'NODE',
        help = 'Output the application list for the given node.')
    return

def add_data_location_options(parser):
    group = parser.add_argument_group('Data location options',
        'Configure where {0} reads in data from. The data location is described in the form of a URI, which '
        'is composed of a resource type and path within the resource, separated by a colon. For example: '
        'yaml_fs:/path/to/data. If the data URI is specified on the command line this overrides any URIs '
        'defined in the configuration file. If given use either --uri or --uri-class and --uri-node'.format(parser.prog))
    group.add_argument('--uri',
        dest = 'uri',
        type = str,
        metavar = 'URI',
        help = 'The URI containing both the nodes and classes data.')
    group.add_argument('--uri-classes',
        dest = 'uri_classes',
        type = str,
        metavar = 'URI',
        help = 'The URI for the classes data.')
    group.add_argument('--uri-nodes',
        dest = 'uri_nodes',
        type = str,
        metavar = 'URI',
        help = 'The URI for the nodes data.')
    return group

def add_output_options(parser):
    group = parser.add_argument_group('Output options',
        'Configure the way {0} prints data.'.format(parser.prog))
    group.add_argument('--log-level',
        dest = 'log_level',
        choices = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'OFF'],
        metavar = 'LEVEL',
        default = cli_default_opts['log_level'],
        help = 'Sets log level. {%(choices)s} (default: %(default)s)')
    return

def make_argparser():
    parser = argparse.ArgumentParser(prog=NAME, description=DESCRIPTION) #, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_run_mode_options(parser)
    add_data_location_options(parser)
    add_output_options(parser)
    parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(VERSION))
    return parser

def cli():
    parser = make_argparser()
    args = parser.parse_args()
    config_file_settings = load_config_file()
