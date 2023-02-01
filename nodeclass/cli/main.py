import sys
from ..exceptions import NodeclassError
from .parser import make_parser
from .command_inventory import command_inventory
from .command_node import command_node
from .command_param import command_param
from .command_version import command_version

COMMANDS = {
    'inventory': command_inventory,
    'node': command_node,
    'param': command_param,
    'version': command_version,
}

def main():
    parser = make_parser()
    args = parser.parse_args()
    try:
        COMMANDS[args.command](args)
    except NodeclassError as exception:
        print(exception)
        sys.exit(1)
