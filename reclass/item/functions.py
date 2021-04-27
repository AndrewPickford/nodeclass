#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
import enum
import pyparsing as pp

Tags = enum.Enum('Tags', ['STR', 'REF', 'INV'])


def tag(name):
    def inner(string, location, tokens):
        return (name, tokens[0])
    return inner


def full_parser(settings):
    '''
    Return the full, but slow parser.

    Only used if more than reference/inv query sentinels are present
    or if the simple single reference parser fails
    '''


    _ESCAPE = settings.escape_character
    _DOUBLE_ESCAPE = _ESCAPE + _ESCAPE

    _REF_OPEN, _REF_CLOSE = settings.reference_sentinels
    _REF_CLOSE_FIRST = _REF_CLOSE[0]
    _REF_ESCAPE_OPEN = _ESCAPE + _REF_OPEN
    _REF_ESCAPE_CLOSE = _ESCAPE + _REF_CLOSE
    _REF_DOUBLE_ESCAPE_OPEN = _DOUBLE_ESCAPE + _REF_OPEN
    _REF_DOUBLE_ESCAPE_CLOSE = _DOUBLE_ESCAPE + _REF_CLOSE
    _REF_EXCLUDES = _ESCAPE + _REF_OPEN + _REF_CLOSE

    _INV_OPEN, _INV_CLOSE = settings.inv_query_sentinels
    _INV_CLOSE_FIRST = _INV_CLOSE[0]
    _INV_ESCAPE_OPEN = _ESCAPE + _INV_OPEN
    _INV_ESCAPE_CLOSE = _ESCAPE + _INV_CLOSE
    _INV_DOUBLE_ESCAPE_OPEN = _DOUBLE_ESCAPE + _INV_OPEN
    _INV_DOUBLE_ESCAPE_CLOSE = _DOUBLE_ESCAPE + _INV_CLOSE

    _EXCLUDES = _ESCAPE + _REF_OPEN + _REF_CLOSE + _INV_OPEN + _INV_CLOSE

    double_escape = pp.Combine(pp.Literal(_DOUBLE_ESCAPE) +
        pp.MatchFirst([pp.FollowedBy(_REF_OPEN),
                       pp.FollowedBy(_REF_CLOSE),
                       pp.FollowedBy(_INV_OPEN),
                       pp.FollowedBy(_INV_CLOSE)])).setParseAction(pp.replaceWith(_ESCAPE))

    ref_open = pp.Literal(_REF_OPEN).suppress()
    ref_close = pp.Literal(_REF_CLOSE).suppress()
    ref_not_open = ~pp.Literal(_REF_OPEN) + ~pp.Literal(_REF_ESCAPE_OPEN) + ~pp.Literal(_REF_DOUBLE_ESCAPE_OPEN)
    ref_not_close = ~pp.Literal(_REF_CLOSE) + ~pp.Literal(_REF_ESCAPE_CLOSE) + ~pp.Literal(_REF_DOUBLE_ESCAPE_CLOSE)
    ref_escape_open = pp.Literal(_REF_ESCAPE_OPEN).setParseAction(pp.replaceWith(_REF_OPEN))
    ref_escape_close = pp.Literal(_REF_ESCAPE_CLOSE).setParseAction(pp.replaceWith(_REF_CLOSE))
    ref_text = pp.CharsNotIn(_REF_EXCLUDES) | pp.CharsNotIn(_REF_CLOSE_FIRST, exact=1)
    ref_content = pp.Combine(pp.OneOrMore(ref_not_open + ref_not_close + ref_text))
    ref_string = pp.MatchFirst([double_escape, ref_escape_open, ref_escape_close, ref_content]).setParseAction(tag(Tags.STR.value))
    ref_item = pp.Forward()
    ref_items = pp.OneOrMore(ref_item)
    reference = (ref_open + pp.Group(ref_items) + ref_close).setParseAction(tag(Tags.REF.value))
    ref_item << (reference | ref_string)

    inv_open = pp.Literal(_INV_OPEN).suppress()
    inv_close = pp.Literal(_INV_CLOSE).suppress()
    inv_not_open = ~pp.Literal(_INV_OPEN) + ~pp.Literal(_INV_ESCAPE_OPEN) + ~pp.Literal(_INV_DOUBLE_ESCAPE_OPEN)
    inv_not_close = ~pp.Literal(_INV_CLOSE) + ~pp.Literal(_INV_ESCAPE_CLOSE) + ~pp.Literal(_INV_DOUBLE_ESCAPE_CLOSE)
    inv_escape_open = pp.Literal(_INV_ESCAPE_OPEN).setParseAction(pp.replaceWith(_INV_OPEN))
    inv_escape_close = pp.Literal(_INV_ESCAPE_CLOSE).setParseAction(pp.replaceWith(_INV_CLOSE))
    inv_text = pp.CharsNotIn(_INV_CLOSE_FIRST)
    inv_content = pp.Combine(pp.OneOrMore(inv_not_close + inv_text))
    inv_string = pp.MatchFirst([double_escape, inv_escape_open, inv_escape_close, inv_content]).setParseAction(tag(Tags.STR.value))
    inv_items = pp.OneOrMore(inv_string)
    inv_query = (inv_open + pp.Group(inv_items) + inv_close).setParseAction(tag(Tags.INV.value))

    text = pp.CharsNotIn(_EXCLUDES) | pp.CharsNotIn('', exact=1)
    content = pp.Combine(pp.OneOrMore(ref_not_open + inv_not_open + text))
    string = pp.MatchFirst([double_escape, ref_escape_open, inv_escape_open, content]).setParseAction(tag(Tags.STR.value))

    item = reference | inv_query | string
    line = pp.OneOrMore(item) + pp.StringEnd()
    return line.leaveWhitespace()


def simple_parser(settings):
    '''
        Return the simple parser which can parse a string with a single reference, eg:

        ${foo}
        foo_${bar}_foo

        To successfully parse one and only one reference is required and no escaped
        reference sentinels are allowed.

        The parser is deliberately simple to process single references as quickly
        as possible.
    '''

    ESCAPE = settings.escape_character
    REF_OPEN, REF_CLOSE = settings.reference_sentinels
    INV_OPEN, INV_CLOSE = settings.inv_query_sentinels
    EXCLUDES = ESCAPE + REF_OPEN + REF_CLOSE + INV_OPEN + INV_CLOSE

    string = pp.CharsNotIn(EXCLUDES).setParseAction(tag(Tags.STR.value))
    ref_open = pp.Literal(REF_OPEN).suppress()
    ref_close = pp.Literal(REF_CLOSE).suppress()
    reference = (ref_open + pp.Group(string) + ref_close).setParseAction(tag(Tags.REF.value))
    line = pp.StringStart() + pp.Optional(string) + reference + pp.Optional(string) + pp.StringEnd()
    return line.leaveWhitespace()
