from typing import NamedTuple
from ..value.hierarchy import Hierarchy

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, List
    from ..utils.url import Url


class KlassID(NamedTuple):
    name: 'str'
    environment: 'str'


class Klass:
    ''' A nodeclass class.
    '''

    @staticmethod
    def from_class_dict(name: 'str', class_dict: 'Dict', url: 'Url') -> 'Klass':
        # It is possible for classes, applications, exports and parameters in the yaml
        # to be None. Change these to an empty list or dict as appropriate.
        applications = class_dict.get('applications', None) or []
        classes = class_dict.get('classes', None) or []
        exports = class_dict.get('exports', None) or {}
        parameters = class_dict.get('parameters', None) or {}
        exports = Hierarchy.from_dict(exports, url, 'exports')
        parameters = Hierarchy.from_dict(parameters, url, 'parameters')
        exports.freeze()
        parameters.freeze()
        return Klass(name, applications, classes, exports, parameters, url)

    def __init__(self, name: 'str', applications: 'List[str]', classes: 'List[str]', exports: 'Hierarchy', parameters: 'Hierarchy', url: 'Url'):
        '''
        name: class name
        applications: list of applications
        classes: list of classes
        exports: Hierarchy of exports
        parameters: Hierarchy of parameters
        url:
        '''
        self.name = name
        self.applications = applications
        self.classes = classes
        self.exports = exports
        self.parameters = parameters
        self.url = url

    def __repr__(self) -> 'str':
        return '{0}(name={1}, url={2}, classes={3}, applications={4}, exports={5}, parameters={6})'.format(
                   self.__class__.__name__, repr(self.name), repr(self.url), repr(self.classes),
                   repr(self.applications), repr(self.exports), repr(self.parameters))

    def __str__(self) -> 'str':
        return '(name={0}, url={1}, classes={2}, applications={3}, exports={4}, parameters={5})'.format(
                   str(self.name), str(self.url), str(self.classes), str(self.applications),
                   str(self.exports), str(self.parameters))
