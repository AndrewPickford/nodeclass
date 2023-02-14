from ..exceptions import InputError, InterpolationError
from ..utils.path import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional
    from ..exceptions import MessageList
    from ..value.value import Value

class InventoryQueryParseError(InputError):
    def __init__(self, description: 'str', expression: 'Optional[str]' = None):
        super().__init__()
        self.expression = expression
        self.description = description

    def message(self) -> 'MessageList':
        self.path = Path.fromlist(self.reverse_path[::-1])
        return super().message() + \
               [ 'Inventory query error: {0}'.format(self.description),
                 'Expression: {0}'.format(self.expression) ]


class InventoryQueryValueNotRenderable(InterpolationError):
    def __init__(self, path: 'Path', value: 'Value'):
        super().__init__()
        self.path = path
        self.value = value

    def message(self) -> 'MessageList':
        return super().message() + \
               [ 'Found unrenderable value: {0}'.format(self.value),
                 'At path: {0}'.format(self.path) ]
