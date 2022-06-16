import pyparsing
import pytest
import nodeclass.invquery.tokenizer as tokenizer
from nodeclass.invquery.exceptions import InventoryQueryParseError
from nodeclass.invquery.parser import parse as parse_expression
from nodeclass.utils.path import Path

expression_tokenizer = tokenizer.make_expression_tokenizer()

VAQ = tokenizer.Tags.VALUE_QUERY.value
IFQ = tokenizer.Tags.IF_QUERY.value
LIQ = tokenizer.Tags.LIST_IF_QUERY.value
OPT = tokenizer.Tags.OPTION.value
IF  = tokenizer.Tags.IF.value
COM = tokenizer.Tags.COMPARISION.value
LOG = tokenizer.Tags.LOGICAL.value
STR = tokenizer.Tags.STRING.value
INT = tokenizer.Tags.INT.value
FLT = tokenizer.Tags.FLOAT.value
EXP = tokenizer.Tags.EXPORT.value
PAR = tokenizer.Tags.PARAMETER.value

Pstr = Path.fromstring

def clean(token):
    '''
    Clean up pyparsing results for easier checking against expected values
    '''
    if isinstance(token, pyparsing.ParseResults):
        return [ clean(t) for t in token.asList() ]
    elif isinstance(token, tokenizer.Token):
        if isinstance(token.data, pyparsing.ParseResults):
            return (token.type, clean(token.data))
    return (token.type, token.data)

invquery_test_data = [
    # Value query
    ( 'exports:alpha',              # expression
      [(VAQ, [(EXP, 'alpha')])],    # expected tokens
      { Pstr('alpha') },            # expected exports
      set() ),                      # expected parameter references

    # If query, exports == self
    ( 'exports:alpha if exports:a:b:c == self:x:y:z',
      [(IFQ, [(EXP, 'alpha'), (IF, 'IF'), (EXP, 'a:b:c'), (COM, '=='), (PAR, 'x:y:z')])],
      { Pstr('alpha'), Pstr('a:b:c') },
      { Pstr('x:y:z') } ),

    # If query, self == exports
    ( 'exports:alpha if self:x:y:z == exports:a:b:c',
      [(IFQ, [(EXP, 'alpha'), (IF, 'IF'), (PAR, 'x:y:z'), (COM, '=='), (EXP, 'a:b:c')])],
      { Pstr('alpha'), Pstr('a:b:c') },
      { Pstr('x:y:z') } ),

    # List if query
    ( 'if exports:a:b:c == self:x:y:z',
      [(LIQ, [(IF, 'IF'), (EXP, 'a:b:c'), (COM, '=='), (PAR, 'x:y:z')])],
      { Pstr('a:b:c') },
      { Pstr('x:y:z') } ),

    # And
    ( 'exports:alpha if exports:a:b == self:x:y and self:u:v != exports:c:d',
      [(IFQ, [(EXP, 'alpha'), (IF, 'IF'), (EXP, 'a:b'), (COM, '=='), (PAR, 'x:y'), (LOG, 'AND'), (PAR, 'u:v'), (COM, '!='), (EXP, 'c:d')])],
      { Pstr('alpha'), Pstr('a:b'), Pstr('c:d') },
      { Pstr('x:y'), Pstr('u:v') } ),

    # Or
    ( 'exports:alpha if exports:a:b == self:x:y or self:u:v == exports:c:d',
      [(IFQ, [(EXP, 'alpha'), (IF, 'IF'), (EXP, 'a:b'), (COM, '=='), (PAR, 'x:y'), (LOG, 'OR'), (PAR, 'u:v'), (COM, '=='), (EXP, 'c:d')])],
      { Pstr('alpha'), Pstr('a:b'), Pstr('c:d') },
      { Pstr('x:y'), Pstr('u:v') } ),
]

# all raise a pyparsing.ParseException
invalid_tokenizer_expressions = [
    # empty expression
    '',
    # misspelled exports
    'expoo:alpha',
    # misspelled if
    'exports:alpha fi exports:a:b == self:x:y',
    # missspelled and
    'exports:alpha if exports:a:b == self:x:y an self:u:v == exports:c:d',
    # missspelled or
    'exports:alpha if exports:a:b == self:x:y ro self:u:v == exports:c:d',
]

# all raise an InventoryQueryParseError exception
invalid_parser_expressions = []
invalid_parser_expressions.extend(invalid_tokenizer_expressions)
invalid_parser_expressions += [
    # two exports in if test
    'if exports:a:b == exports:x:y',
    # two selfs in if test
    'if self:a:b == self:x:y',
    # missing and/or
    'if exports:a:b == self:x:y exports:c:d == self:c:d',
    # doubled and/or
    'if exports:a:b == self:x:y and and exports:c:d == self:c:d',
    'if exports:a:b == self:x:y and or exports:c:d == self:c:d',
    'if exports:a:b == self:x:y or or exports:c:d == self:c:d',
    # missing if
    'exports:a:b == self:x:y',
    # two ifs
    'if if exports:a:b == self:x:y',
]

tokenizer_test_data = [ (expression, tokens) for expression, tokens, exports, parameters in invquery_test_data ]
parser_test_data = [ (expression, exports, parameters) for expression, tokens, exports, parameters in invquery_test_data ]

@pytest.mark.parametrize('expression, expected', tokenizer_test_data)
def test_expression_tokenizer(expression, expected):
    result = clean(expression_tokenizer.parseString(expression))
    assert result == expected

@pytest.mark.parametrize('expression', invalid_tokenizer_expressions)
def test_expression_tokenizer_exceptions(expression):
    with pytest.raises(pyparsing.ParseException):
        expression_tokenizer.parseString(expression)

@pytest.mark.parametrize('expression, exports, parameters', parser_test_data)
def test_query(expression, exports, parameters):
    query = parse_expression(expression)
    assert query.exports == exports
    assert query.references == parameters

@pytest.mark.parametrize('expression', invalid_parser_expressions)
def test_expression_parser_exceptions(expression):
    with pytest.raises(InventoryQueryParseError) as info:
        parse_expression(expression)
    assert info.value.expression == expression
