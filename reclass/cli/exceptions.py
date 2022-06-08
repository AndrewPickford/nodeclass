from ..exceptions import ConfigError


class BadArguments(ConfigError):
    def __init__(self, message):
        super().__init__()
        self.error_message = message

    def message(self):
        return super().message() + [ 'Invalid command line arguments: {0}'.format(self.error_message) ]


class NoInventoryUri(ConfigError):
    def __init__(self):
        super().__init__()

    def message(self):
        return super().message() + [ 'No location for inventory specified' ]
