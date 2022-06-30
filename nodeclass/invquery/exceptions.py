from __future__ import annotations

from ..exceptions import InputError
from ..utils.path import Path


class InventoryQueryParseError(InputError):
    def __init__(self, description: str, expression: str|None = None):
        super().__init__()
        self.expression = expression
        self.description = description

    def message(self) -> list[str]:
        self.path = Path.fromlist(self.reverse_path[::-1])
        return super().message() + \
               [ 'Inventory query error: {0}'.format(self.description),
                 'Expression: {0}'.format(self.expression) ]
