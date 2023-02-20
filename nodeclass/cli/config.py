import collections
from ..config_file import load_config_file
from ..exceptions import UnknownConfigSetting
from ..settings import Settings
from ..storage.uri import Uri
from .exceptions import BadArguments, NoInventoryUri

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import argparse
    from typing import Tuple, Union
    from ..settings import ConfigDict


ARG_SETTINGS_KEYS = [ 'env_override' ]


def process_config_file_and_args(args: 'argparse.Namespace') -> 'Tuple[Settings, Uri]':
    if args.config_filename:
        filename = args.config_filename
        search_path = [ '.', '/' ]
    else:
        filename = None
        search_path = None
    settings_config_file, uri_config_file, filename = load_config_file(filename=filename, search_path=search_path)
    settings_config_args, uri_config_args = process_args(args)
    try:
        settings = Settings(collections.ChainMap(settings_config_args, settings_config_file))
    except UnknownConfigSetting as exception:
        if exception.name in settings_config_file:
            exception.location = filename
        elif exception.name in settings_config_args:
            exception.location = 'command line arguments'
        raise
    if uri_config_args:
        uri = Uri(uri_config_args, 'commandline arguments')
    elif uri_config_file:
        uri = Uri(uri_config_file, filename)
    else:
        raise NoInventoryUri()
    return settings, uri

def get_uri(args: 'argparse.Namespace') -> 'Union[ConfigDict, str, None]':
    if args.uri:
        if args.uri_classes:
            raise BadArguments('both --uri and --uri-classes specified')
        if args.uri_nodes:
            raise BadArguments('both --uri and --uri-nodes specified')
        return args.uri
    if args.uri_classes and args.uri_nodes == None:
        raise BadArguments('--uri-classes specified, but not --uri-nodes')
    if args.uri_classes == None and args.uri_nodes:
        raise BadArguments('--uri-nodes specified, but not --uri-classes')
    if args.uri_classes and args.uri_nodes:
        return { 'classes': args.uri_classes, 'nodes': args.uri_nodes }
    return None

def process_args(args: 'argparse.Namespace') -> 'Tuple[ConfigDict, Union[ConfigDict, str, None]]':
    vargs = vars(args)
    settings = { k: vargs[k] for k in ARG_SETTINGS_KEYS if k in vargs }
    uri = get_uri(args)
    return settings, uri
