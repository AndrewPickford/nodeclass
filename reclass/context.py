import contextlib
import copy
import re
import threading
from .item.tokenizer import make_full_tokenizer, make_simple_tokenizer
from .invquery.tokenizer import make_expression_tokenizer
from .settings import Settings

def reclass_set_context(settings):
    CONTEXT.settings = copy.copy(settings)
    CONTEXT.delimiter = settings.delimiter
    CONTEXT.path_split = r'(?<!\\)' + re.escape(CONTEXT.delimiter)
    CONTEXT.prefixes = { settings.immutable_prefix, settings.overwrite_prefix }
    CONTEXT.full_tokenizer = make_full_tokenizer(CONTEXT.settings)
    CONTEXT.simple_tokenizer = make_simple_tokenizer(CONTEXT.settings)
    CONTEXT.expression_tokenizer = make_expression_tokenizer()
    CONTEXT.item_parse_cache = {}

@contextlib.contextmanager
def reclass_context(settings):
    old_settings = CONTEXT.settings
    old_delimiter = CONTEXT.delimiter
    old_path_split = CONTEXT.path_split
    old_prefixes = CONTEXT.prefixes
    old_full_tokenizer = CONTEXT.full_tokenizer
    old_simple_tokenizer = CONTEXT.simple_tokenizer
    old_expression_tokenizer = CONTEXT.expression_tokenizer
    old_item_parse_cache = CONTEXT.item_parse_cache
    reclass_set_context(settings)
    yield
    CONTEXT.settings = old_settings
    CONTEXT.delimiter = old_delimiter
    CONTEXT.path_split = old_path_split
    CONTEXT.prefixes = old_prefixes
    CONTEXT.full_tokenizer = old_full_tokenizer
    CONTEXT.simple_tokenizer = old_simple_tokenizer
    CONTEXT.expression_tokenizer = old_expression_tokenizer
    CONTEXT.item_parse_cache = old_item_parse_cache
    return

CONTEXT = threading.local()
reclass_set_context(Settings())
