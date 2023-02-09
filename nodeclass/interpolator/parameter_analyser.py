import copy
from ..utils.path import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable, List, Tuple
    from ..value.hierarchy import Hierarchy

class ParameterAnalyser:
    def __init__(self, parameter: 'Path'):
        self.parameter = parameter
        self.merge_history: 'List[Tuple[Hierarchy, Hierarchy, Hierarchy]]' = []

    def hierarchy_merge_wrapper(self, first: 'Hierarchy', second: 'Hierarchy', merge_function: 'Callable'):
        first.set_copy_on_change()
        second.set_copy_on_change()
        original_first = copy.copy(first)
        original_second = copy.copy(second)
        merge_function()
        first.set_copy_on_change()
        self.merge_history.append((original_first, original_second, first))

    def print_report(self):
        print('Analysis for parameter:{0}'.format(self.parameter))
        if len(self.merge_history) == 0:
            print('** NO DATA **')
            return
        found = False
        initial, _, _ = self.merge_history[0]
        if self.parameter in initial:
            found = True
            print(initial.url.name, initial[self.parameter].description())
        for entry in self.merge_history:
            first, second, result = entry
            if self.parameter in second:
                if found:
                    print(second.url.name, second[self.parameter].description(), result[self.parameter].description())
                else:
                   found = True
                   print(second.url.name, second[self.parameter].description())
