from reclass.utils.path import Path
from .exceptions import InventoryQueryParseError
from .parser_functions import Tags


class Operand:
    def __init__(self, token):
        if token.type not in [ Tags.STRING.value, Tags.INT.value, Tags.FLOAT.value, Tags.EXPORT.value, Tags.PARAMETER.value ]:
            raise InventoryQueryParseError(token, 'unknown operand {0}'.format(token.data))
        self.type = token.type
        if self.type in [ Tags.EXPORT.value, Tags.PARAMETER.value ]:
            self.data = token.data[1].data
        elif token.type in [ Tags.STRING.value, Tags.INT.value, Tags.FLOAT.value ]:
            self.data = token.data
        else:
            InventoryQueryParseError(token, 'unknown operand {0}'.format(token.data))
        if self.type in [ Tags.EXPORT.value, Tags.PARAMETER.value ]:
            self.path = Path.fromstring(self.data)
        else:
            self.path = None

    def __eq_(self, other):
        if self.__class__ == other.__class__:
            if self.type == other.type and self.data == other.data:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self.type == Tags.EXPORT.value:
            return 'exports:{0}'.format(self.data)
        elif self.type == Tags.PARAMETER.value:
            return 'parameters:{0}'.format(self.data)
        else:
            return str(self.data)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, str(self))

    @property
    def exports(self):
        if self.type == Tags.EXPORT.value:
            return { Path.fromstring(self.data) }
        return set()

    @property
    def references(self):
        if self.type == Tags.PARAMETER.value:
            return { Path.fromstring(self.data) }
        return set()
