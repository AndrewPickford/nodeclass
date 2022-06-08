from ..exceptions import ProcessError
from ..utils.path import Path

class InventoryQueryParseError(ProcessError):
    def __init__(self, description, expression=None, tokens=None):
        super().__init__()
        self.expression = expression
        self.tokens = tokens
        self.description = description

    def message(self):
        self.path = Path.fromlist(self.reverse_path[::-1])
        return super().message() + \
               [ 'Inventory query error: {0}'.format(self.description),
                 'Expression: {0}'.format(self.expression) ]
