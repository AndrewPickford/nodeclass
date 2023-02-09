from ..exceptions import ConfigError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..exceptions import MessageList


class BadArguments(ConfigError):
    def __init__(self, message):
        super().__init__()
        self.error_message = message

    def message(self) -> 'MessageList':
        return super().message() + [ 'Invalid command line arguments: {0}'.format(self.error_message) ]


class NoInventoryUri(ConfigError):
    def __init__(self):
        super().__init__()

    def message(self) -> 'MessageList':
        return super().message() + [ 'No location for inventory specified' ]
