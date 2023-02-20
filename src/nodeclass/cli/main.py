import sys
import yaml
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

def str_presenter(dumper, data):
    '''
        Configure yaml for dumping multiline strings
        Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
    '''
    if data.count('\n') > 0:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)
yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

def main():
    parser = make_parser()
    args = parser.parse_args()
    try:
        COMMANDS[args.command](args)
    except NodeclassError as exception:
        print(exception)
        sys.exit(1)
