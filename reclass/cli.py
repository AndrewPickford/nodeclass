import argparse
from .config_file import load_config_file
from .version import NAME, DESCRIPTION, VERSION

cli_default_opts = {
    'log_level': 'OFF',
}

def add_output_options(parser):
    group = parser.add_argument_group('Output options',
        'Configure the way {0} prints data'.format(parser.prog))

    group.add_argument('--log',
        dest = 'log_level',
        default = cli_default_opts['log_level'],
        choices = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'OFF'],
        metavar = 'LEVEL',
        help = 'Turns off normal output and prints logging output. {%(choices)s}')
    return

def make_argparser():
    parser = argparse.ArgumentParser(prog=NAME, description=DESCRIPTION, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(VERSION))
    add_output_options(parser)
    return parser

def cli():
    parser = make_argparser()
    args = parser.parse_args()
    config_file_settings = load_config_file()
