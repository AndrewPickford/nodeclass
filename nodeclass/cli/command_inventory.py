import yaml
import nodeclass.core as core
from ..context import nodeclass_set_context
from ..exceptions import MultipleNodeErrors
from ..storage.exceptions import InvalidUri
from .config import process_config_file_and_args

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import argparse
    from ..storage.uri import Uri


def nodeinfos(uri: 'Uri', directory: 'str'):
    nodeinfos, exceptions = core.nodeinfo_all(uri)
    for nodeinfo in nodeinfos:
        filename = '{0}/{1}.yml'.format(directory, nodeinfo.name)
        with open(filename, 'w') as file:
            yaml.dump(nodeinfo.as_dict(), file, default_flow_style=False, Dumper=yaml.CSafeDumper)
    if len(exceptions) > 0:
        raise MultipleNodeErrors(exceptions)

def command_inventory(args: 'argparse.Namespace'):
    settings, uri = process_config_file_and_args(args)
    nodeclass_set_context(settings)
    try:
        nodeinfos(uri, args.output)
    except InvalidUri as exception:
        exception.location = uri.location
        raise
