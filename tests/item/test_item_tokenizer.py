import pyparsing
import pytest
import nodeclass.item.tokenizer as tokenizer
from nodeclass.item.parser import parse as parse_expression
from nodeclass.settings import Settings
from nodeclass.utils.path import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, List, Set, Tuple

settings = Settings()
simple_tokenizer = tokenizer.make_simple_tokenizer(settings)
full_tokenizer = tokenizer.make_full_tokenizer(settings)

INV = tokenizer.Tag.INV.value
REF = tokenizer.Tag.REF.value
STR = tokenizer.Tag.STR.value

Pstr = Path.fromstring

def clean(token):
    '''
    Clean up pyparsing results for easy checking against expected values
    '''
    if isinstance(token, pyparsing.ParseResults):
        token = token.asList()
        return [ clean(t) for t in token ]
    elif isinstance(token, tuple):
        if isinstance(token[1], pyparsing.ParseResults):
            return (token[0], clean(token[1]) )
    return token

test_data_simple: 'List[Tuple[str, Any, Set[Path]]]' = [
    # Basic test cases.
    ( '${foo}',                      # expression
      [(REF, [(STR, 'foo')])],       # tokens
      { Pstr('foo') } ),             # references

    # Basic combinations.
    ( 'bar${foo}',
      [(STR, 'bar'), (REF, [(STR, 'foo')])],
      { Pstr('foo') } ),

    ( 'bar${foo}baz',
      [(STR, 'bar'), (REF, [(STR, 'foo')]), (STR, 'baz')],
      { Pstr('foo') } ),

    ( '${foo}baz',
      [(REF, [(STR, 'foo')]), (STR, 'baz')],
      { Pstr('foo') } ),

    # Whitespace preservation cases.
    ( 'bar ${foo}',
      [(STR, 'bar '), (REF, [(STR, 'foo')])],
      { Pstr('foo') } ),

    ( 'bar ${foo baz}',
      [(STR, 'bar '), (REF, [(STR, 'foo baz')])],
      { Pstr('foo baz') } ),

    ( 'bar${foo} baz',
      [(STR, 'bar'), (REF, [(STR, 'foo')]), (STR, ' baz')],
      { Pstr('foo') } ),

    ( ' bar${foo} baz ',
      [(STR, ' bar'), (REF, [(STR, 'foo')]), (STR, ' baz ')],
      { Pstr('foo') } ),
]

test_data_complex: 'List[Tuple[str, Any, Set[Path]]]' = [
    # Single elements sanity check.
    ( 'foo',
      [(STR, 'foo')],
      set() ),

    ( '$foo',
      [(STR, '$foo')],
      set() ),

    ( '{foo}',
      [(STR, '{foo}')],
      set() ),

    ( '[foo]',
      [(STR, '[foo]')],
      set() ),

    ( '$(foo)',
      [(STR, '$(foo)')],
      set() ),

    ( '$[exports:foo]',
      [(INV, [(STR, 'exports:foo')])],
      set() ),

    # Escape sequences.
    ( r'\${foo}',
      [(STR, '${'), (STR, 'foo}')],
      set() ),
    # Note the double backslashes '\\' below which python reduces to a
    # single backslash
    ( r'\\${foo}',
      [(STR, '\\'), (REF, [(STR, 'foo')])],
      { Pstr('foo') } ),
    # This is probably not what would be expected. With \\\\$ the backslash closest to the $ sign
    # is removed and the rest pass through.
    # SHOULD THIS BE CHANGED?
    #(r'\\\\${foo}', [(pf.tag.STR, r'\\'), (pf.tag.STR, '\\'), (pf.tag.REF, [(pf.tag.STR, 'foo')])]),

    # Whitespace preservation in various positions.
    ( ' foo ',
      [(STR, ' foo ')],
      set() ),

    ( 'foo bar',
      [(STR, 'foo bar')],
      set() ),

    # Compound references
    ( '${foo}${bar}',
      [(REF, [(STR, 'foo')]), (REF, [(STR, 'bar')])],
      { Pstr('foo'), Pstr('bar') } ),

    # Nested references
    ( '${foo${bar}}',
      [(REF, [(STR, 'foo'), (REF, [(STR, 'bar')])])],
      { Pstr('bar') } ), # Only the reference to bar is initially present after parsing

    ( '${foo${bar${baz}}}',
      [(REF, [(STR, 'foo'), (REF, [(STR, 'bar'), (REF, [(STR, 'baz')])])])],
      { Pstr('baz') } ),  # Only the reference to baz is initially present after parsing

    # Reference with nested inventory query, which parses to a reference to the literal
    # string of inventory query. This is fine, inventory queries can not be nested inside
    # references.
    ( '${$[foo]}',
      [(REF, [(STR, '$[foo]')])],
      { Pstr('$[foo]') } ),
]

test_data_tokenizer_only: 'List[Tuple[str, Any, Set[Path]]]' = [
    # Inventory queries with nested references will be parsed to an inventory
    # query containing a string of the nested items. These will later fail the
    # inventory query expression parser.
    # WOULD BE BETTER IF THIS RAISED AN EXCEPTION IN THE PARSER
    ( '$[${foo}]',
      [(INV, [(STR, '${foo}')])],
      set() ),
]

simple_tokenizer_test_errors = [
    # The simple parser does not parse multiple references or inventory queries
    '${foo}${bar}', '$[foo]'
]

full_tokenizer_test_errors = [
    # Nested inventory queries are not allowed
    '$[foo$[bar]]',

    # An inventory query cannot be combined with anything else
    'bar$[foo]', 'bar$[foo]baz', '$[foo]baz',
    '${bar}$[foo]', '${bar}$[foo]${baz}', '$[foo]${baz}',
]

a = test_data_simple + test_data_complex

tokenizer_simple_test_data = [ (expression, tokens) for expression, tokens, references in test_data_simple ]
tokenizer_full_test_data = [ (expression, tokens) for expression, tokens, references in test_data_simple + test_data_complex + test_data_tokenizer_only ]
parser_test_data = [ (expression, references) for expression, tokens, references in test_data_simple + test_data_complex ]

@pytest.mark.parametrize('expression, expected', tokenizer_simple_test_data)
def test_simple_item_tokenizer(expression, expected):
    result = clean(simple_tokenizer.parseString(expression))
    assert result == expected

@pytest.mark.parametrize('expression, expected', tokenizer_full_test_data)
def test_full_item_tokenizer(expression, expected):
    result = clean(full_tokenizer.parseString(expression))
    assert result == expected

@pytest.mark.parametrize('expression', simple_tokenizer_test_errors)
def test_simple_item_tokenizer_errors(expression):
    with pytest.raises(pyparsing.ParseException):
        simple_tokenizer.parseString(expression)

@pytest.mark.parametrize('expression', full_tokenizer_test_errors)
def test_full_item_tokenizer_errors(expression):
    with pytest.raises(pyparsing.ParseException):
        full_tokenizer.parseString(expression)

@pytest.mark.parametrize('expression, references', parser_test_data)
def test_item_parser(expression, references):
    query = parse_expression(expression)
    assert query.references == references
