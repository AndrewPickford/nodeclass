import pyparsing as pp
import pytest
import reclass.item.parser_functions as parser_functions
from reclass.settings import Settings

settings = Settings()
simple_parser = parser_functions.simple_parser(settings)
full_parser = parser_functions.full_parser(settings)

INV = parser_functions.Tags.INV.value
REF = parser_functions.Tags.REF.value
STR = parser_functions.Tags.STR.value

def clean(token):
    '''
    Clean up pyparsing results for easy checking against expected values
    '''
    if isinstance(token, pp.ParseResults):
        token = token.asList()
        return [ clean(t) for t in token ]
    elif isinstance(token, tuple):
        if isinstance(token[1], pp.ParseResults):
            return (token[0], clean(token[1]) )
    return token

test_simple_parser = (
    # Basic test cases.
    ('${foo}', [(REF, [(STR, 'foo')])]),

    # Basic combinations.
    ('bar${foo}', [(STR, 'bar'), (REF, [(STR, 'foo')])]),
    ('bar${foo}baz', [(STR, 'bar'), (REF, [(STR, 'foo')]), (STR, 'baz')]),
    ('${foo}baz', [(REF, [(STR, 'foo')]), (STR, 'baz')]),

    # Whitespace preservation cases.
    ('bar ${foo}', [(STR, 'bar '), (REF, [(STR, 'foo')])]),
    ('bar ${foo baz}', [(STR, 'bar '), (REF, [(STR, 'foo baz')])]),
    ('bar${foo} baz', [(STR, 'bar'), (REF, [(STR, 'foo')]), (STR, ' baz')]),
    (' bar${foo} baz ', [(STR, ' bar'), (REF, [(STR, 'foo')]), (STR, ' baz ')]),
)

test_full_parser = test_simple_parser
test_full_parser += (
    # Single elements sanity.
    ('foo', [(STR, 'foo')]),
    ('$foo', [(STR, '$foo')]),
    ('{foo}', [(STR, '{foo}')]),
    ('[foo]', [(STR, '[foo]')]),
    ('$(foo)', [(STR, '$(foo)')]),
    ('$[foo]', [(INV, [(STR, 'foo')])]),

    # Escape sequences.
    (r'\${foo}', [(STR, '${'), (STR, 'foo}')]),
    # Note the double backslashes '\\' below which python reduces to a
    # single backslash
    (r'\\${foo}', [(STR, '\\'), (REF, [(STR, 'foo')])]),
    # This is probably not would be expected. With \\\\$ the backslash closest to the $ sign
    # is removed and the rest pass through.
    # SHOULD THIS BE CHANGED?
    #(r'\\\\${foo}', [(pf.tags.STR, r'\\'), (pf.tags.STR, '\\'), (pf.tags.REF, [(pf.tags.STR, 'foo')])]),

    # Whitespace preservation in various positions.
    (' foo ', [(STR, ' foo ')]),
    ('foo bar', [(STR, 'foo bar')]),

    # Compound references
    ('${foo}${bar}', [(REF, [(STR, 'foo')]), (REF, [(STR, 'bar')])]),

    # Nested references
    ('${foo${bar}}',[(REF, [(STR, 'foo'), (REF, [(STR, 'bar')])])]),
    ('${foo${bar${baz}}}',[(REF, [(STR, 'foo'), (REF, [(STR, 'bar'), (REF, [(STR, 'baz')])])])]),

    # Reference with nested inventory query, which parses to a reference to the literal
    # string of inventory query. This is fine, inventory queries can not be nested inside
    # references.
    ('${$[foo]}', [(REF, [(STR, '$[foo]')])]),

    # Inventory queries with nested references will be parsed to an inventory
    # query containing a string of the nested items. These will later fail the
    # inventory query expression parser.
    # WOULD BE BETTER IF THIS RAISED AN EXCEPTION IN THE PARSER
    ('$[${foo}]', [(INV, [(STR, '${foo}')])]),
)

test_simple_parser_errors = [
    # The simple parser does not parse multiple references or inventory queries
    '${foo}${bar}', '$[foo]'
]

test_full_parser_errors = [
    # Nested inventory queries are not allowed
    '$[foo$[bar]]',

    # An inventory query cannot be combined with anything else
    'bar$[foo]', 'bar$[foo]baz', '$[foo]baz',
    '${bar}$[foo]', '${bar}$[foo]${baz}', '$[foo]${baz}',
]


@pytest.mark.parametrize('string, expected', test_simple_parser)
def test_simple_item_parser(string, expected):
    result = clean(simple_parser.parseString(string))
    assert result == expected

@pytest.mark.parametrize('string, expected', test_full_parser)
def test_full_item_parser(string, expected):
    result = clean(full_parser.parseString(string))
    assert result == expected

@pytest.mark.parametrize('string', test_simple_parser_errors)
def test_simple_parser_errors(string):
    with pytest.raises(pp.ParseException):
        simple_parser.parseString(string)

@pytest.mark.parametrize('string', test_full_parser_errors)
def test_full_parser_errors(string):
    with pytest.raises(pp.ParseException):
        full_parser.parseString(string)
