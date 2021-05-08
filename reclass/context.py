import contextlib
import copy
import re
import threading
from .settings import Settings

def reclass_set_context(settings):
    from .item.parser import Parser as ItemParser
    CONTEXT.settings = copy.copy(settings)
    CONTEXT.delimiter = settings.delimiter
    CONTEXT.path_split = r'(?<!\\)' + re.escape(CONTEXT.delimiter)
    CONTEXT.item_parser = ItemParser(CONTEXT.settings)

@contextlib.contextmanager
def reclass_context(settings):
    old_settings = CONTEXT.settings
    reclass_set_context(settings)
    yield
    reclass_set_context(old_settings)
    return

CONTEXT = threading.local()
reclass_set_context(Settings())
