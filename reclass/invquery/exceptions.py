class InventoryQueryParseError(Exception):
    def __init__(self, tokens, description):
        super().__init__()
        self.tokens = tokens
        self.description = description
