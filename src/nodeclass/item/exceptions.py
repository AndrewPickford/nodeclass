#
# -*- coding: utf-8 -*-
#
# This file is part of nodeclass
#
from ..exceptions import InputError, InterpolationError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any
    from ..exceptions import MessageList
    from .invquery import InvQuery
    from .item import Item
    from .reference import Reference
    from .scalar import Scalar
    from .tokenizer import Tag


class ItemError(InterpolationError):
    def __init__(self, item: 'Item'):
        super().__init__()
        self.item = item

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Item: {0}'.format(self.item) ]


class InvQueryRender(ItemError):
    def __init__(self, item: 'InvQuery'):
        super().__init__(item)

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Internal error: InvQuery reached render' ] + \
               self.traceback()


class InvQueryResolveToItem(ItemError):
    def __init__(self, item: 'InvQuery'):
        super().__init__(item)

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Internal error: InvQuery reached resolve_to_item' ] + \
               self.traceback()


class ReferenceRender(ItemError):
    def __init__(self, item: 'Reference'):
        super().__init__(item)

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Internal error: Reference reached render' ] + \
               self.traceback()


class ScalarResolveToValue(ItemError):
    def __init__(self, item: 'Scalar'):
        super().__init__(item)

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Internal error: Scalar reached resolve to value' ] + \
               self.traceback()


class ItemResolveError(ItemError):
    def __init__(self, item: 'Item'):
        super().__init__(item)

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Item resolve error' ]


class ParseError(InputError):
    def __init__(self, input: 'str', location: 'int'):
        super().__init__()
        self.input = input
        self.location = location

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Parse error',
                 'Position: {0}'.format(self.location),
                 'Input: {0}'.format(self.input) ]


class BadParseToken(InputError):
    def __init__(self, tag: 'Tag', value: 'Any'):
        super().__init__()
        self.tag = tag
        self.value = value

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Bad parse token',
                 'Tag: {0}'.format(self.tag),
                 'Value: {0}'.format(self.value) ] + \
               self.traceback()
