from ..exceptions import InputError
from ..utils.path import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Optional


class InventoryQueryParseError(InputError):
    def __init__(self, description: 'str', expression: 'Optional[str]' = None):
        super().__init__()
        self.expression = expression
        self.description = description

    def message(self) -> 'List[str]':
        self.path = Path.fromlist(self.reverse_path[::-1])
        return super().message() + \
               [ 'Inventory query error: {0}'.format(self.description),
                 'Expression: {0}'.format(self.expression) ]
