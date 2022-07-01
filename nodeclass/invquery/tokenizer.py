#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from __future__ import annotations

import enum
import pyparsing as pp
from collections import namedtuple


Tag = enum.Enum('Tag', ['VALUE_QUERY', 'IF_QUERY', 'LIST_IF_QUERY', 'OPTION', 'IF',
    'COMPARISION', 'LOGICAL', 'STRING', 'BOOL', 'INT', 'FLOAT', 'EXPORT', 'PARAMETER'])

Token = namedtuple('Token', ['type', 'data'])

_TRUE = 'true'
_FALSE = 'false'

def tag(name):
    def inner(string, location, tokens):
        return Token(name, tokens[0])
    return inner

def tag_to_bool(name):
    def inner(string, location, tokens):
        if tokens[0].lower() == _TRUE:
            return Token(name, True)
        return Token(name, False)
    return inner

def tag_to_int(name):
    def inner(string, location, tokens):
        return Token(name, int(tokens[0]))
    return inner

def tag_to_float(name):
    def inner(string, location, tokens):
        return Token(name, float(tokens[0]))
    return inner

def tag_to_lower(name):
    def inner(string, location, tokens):
        return Token(name, tokens[0].lower())
    return inner


def make_expression_tokenizer():
    '''
    '''
    _IGNORE_ERRORS = '+IgnoreErrors'
    _ALL_ENVS = '+AllEnvs'
    _IF = 'IF'
    _EQUAL = '=='
    _NOT_EQUAL = '!='
    _AND = 'AND'
    _OR = 'OR'
    _EXPORT = 'exports:'
    _PARAMETER = ('self:', 'parameters:')

    ignore_errors = pp.CaselessLiteral(_IGNORE_ERRORS)
    all_envs = pp.CaselessLiteral(_ALL_ENVS)
    option = (ignore_errors | all_envs).setParseAction(tag_to_lower(Tag.OPTION.value))
    options = pp.ZeroOrMore(option)

    op_eq = pp.Literal(_EQUAL)
    op_neq = pp.Literal(_NOT_EQUAL)
    op_and = pp.CaselessLiteral(_AND)
    op_or = pp.CaselessLiteral(_OR)
    operator_test = (op_eq | op_neq).setParseAction(tag(Tag.COMPARISION.value))
    operator_logical = (op_and | op_or).setParseAction(tag(Tag.LOGICAL.value))
    begin_if = pp.CaselessLiteral(_IF).setParseAction(tag(Tag.IF.value))

    quoted_string = pp.QuotedString('\'"')
    string = pp.Word(pp.printables)
    quoted_string_tagged = pp.QuotedString('\'"').setParseAction(tag(Tag.STRING.value))
    string_tagged = pp.Word(pp.printables).setParseAction(tag(Tag.STRING.value))

    export = pp.CaselessLiteral(_EXPORT).suppress() + (quoted_string | string).setParseAction(tag(Tag.EXPORT.value))
    parameter = (pp.CaselessLiteral(_PARAMETER[0]) | pp.CaselessLiteral(_PARAMETER[1])).suppress() + (quoted_string | string).setParseAction(tag(Tag.PARAMETER.value))

    bool = (pp.CaselessLiteral(_TRUE) | pp.CaselessLiteral(_FALSE)).setParseAction(tag_to_bool(Tag.BOOL.value))
    sign = pp.Optional(pp.Literal('-'))
    number = pp.Word(pp.nums)
    dpoint = pp.Literal('.')
    real_abs = ((number + dpoint + number) | (dpoint + number) | (number + dpoint))
    real = pp.Combine(sign + real_abs).setParseAction(tag_to_float(Tag.FLOAT.value))
    integer = pp.Combine(sign + number + pp.WordEnd()).setParseAction(tag_to_int(Tag.INT.value))

    expritem = bool | integer | real | quoted_string_tagged | export | parameter | string_tagged
    single_test = expritem + operator_test + expritem
    additional_test = operator_logical + single_test
    if_test = begin_if + single_test + pp.ZeroOrMore(additional_test)

    expr_var = pp.Group(export).setParseAction(tag(Tag.VALUE_QUERY.value))
    expr_test = pp.Group(export + if_test).setParseAction(tag(Tag.IF_QUERY.value))
    expr_list_test = pp.Group(if_test).setParseAction(tag(Tag.LIST_IF_QUERY.value))
    expr = expr_test | expr_var | expr_list_test
    line = pp.StringStart() + options + expr + pp.StringEnd()
    return line
