class ReclassError(Exception):
    def __init__(self):
        super().__init__()


class ReclassRuntimeError(ReclassError):
    def __init__(self, message):
        super().__init__()
        if isinstance(message, str):
            self.message = [ (0, message) ]
        else:
            self.message = message
