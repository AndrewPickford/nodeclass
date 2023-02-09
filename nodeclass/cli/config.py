import collections
from typing import NamedTuple
from ..config_file import load_config_file
from ..exceptions import UnknownConfigSetting
from ..settings import Settings
from .exceptions import BadArguments, NoInventoryUri

class URI(NamedTuple):
    config: 'str'
    location: 'str'

ARG_SETTINGS_KEYS = [ 'env_override' ]

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

def get_uri(args):
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

def process_args(args):
    vargs = vars(args)
    settings = { k: vargs[k] for k in ARG_SETTINGS_KEYS if k in vargs }
    uri = get_uri(args)
    return settings, uri
