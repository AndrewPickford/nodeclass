class InventoryQueryParseError(Exception):
    def __init__(self, description, expression=None, tokens=None):
        super().__init__()
        self.expression = expression
        self.tokens = tokens
        self.description = description
