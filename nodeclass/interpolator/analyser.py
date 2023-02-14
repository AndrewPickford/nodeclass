from abc import ABC, abstractmethod

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable
    from ..value.hierarchy import Hierarchy


class Analyser(ABC):
    @abstractmethod
    def hierarchy_merge_wrapper(self, first: 'Hierarchy', second: 'Hierarchy', merge_function: 'Callable'):
        '''
        '''
        pass
