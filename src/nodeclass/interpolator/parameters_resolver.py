import copy
from collections import defaultdict
from ..exceptions import InterpolationError
from ..utils.path import Path
from ..value.exceptions import NoSuchPath
from .exceptions import ExcessivePathRevisits, CircularReference, InterpolateUnhandledError, MergableInterpolationError, MultipleInterpolationErrors, NoSuchReference

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict
    from ..value.hierarchy import Hierarchy
    from ..value.value import Value
    from .inventory import InventoryDict


class ParametersResolver:
    '''
    '''

    def resolve(self, environment: 'str', parameters: 'Hierarchy', inventory: 'InventoryDict') -> 'Hierarchy':
        '''
        environment: Environment to resolve the parameters in
        parameters: Hierarchy of already merged parameters to resolve
        inventory: Hierarchy of pre-evaluated inventory query answers
        returns: Hierarchy of resolved parameters
        '''
        self.environment = environment
        self.parameters = copy.copy(parameters)
        self.inventory = inventory
        self.visit_count: 'Dict[Path, int]' = defaultdict(int)
        self.unresolved = dict.fromkeys(self.parameters.unresolved_paths(), False)
        self.interpolation_exceptions: 'Dict[Path, MergableInterpolationError]' = {}
        self.resolve_unresolved_paths()
        if len(self.interpolation_exceptions) > 0:
            raise MultipleInterpolationErrors(list(self.interpolation_exceptions.values()))
        return self.parameters

    def resolve_unresolved_paths(self):
        while len(self.unresolved) > 0:
            path = next(iter(self.unresolved))
            try:
                self.resolve_path(path)
            except MergableInterpolationError as exception:
                if exception.path in self.interpolation_exceptions:
                    raise MultipleInterpolationErrors(list(self.interpolation_exceptions.values()))
                else:
                    exception.category = 'parameters'
                    self.interpolation_exceptions[path] = exception
                    del self.unresolved[path]
            except InterpolationError as exception:
                exception.category = 'parameters'
                raise
        return

    def resolve_path(self, path: 'Path'):
        '''
        Resolve (dereference and/or merge) the Value at the given path, by repeatedly
        calling resolve_value until:
            the Value resolves
            we revisit this path and hence have circular references
            the visit count for the Value at this path is exceeded
        '''
        self.unresolved[path] = True
        if self.parameters.unresolved_ancestor(path):
            self.resolve_path(path.parent())
        value = self.parameters[path]
        while value.unresolved:
            value = self.resolve_value(path, value)
        new_paths = value.unresolved_paths(path)
        if new_paths:
            self.unresolved.update(dict.fromkeys(new_paths, False))
        self.parameters[path] = value
        del self.unresolved[path]
        return

    def resolve_value(self, path: 'Path', value: 'Value'):
        '''
        Remove one level of indirection

        If this method needs to be called a second time for a given path keep a count
        of the number of times this method has been called for the path and raise an
        error if the visit count threshold is exceeded.
        '''
        for reference in value.references:
            if reference in self.unresolved:
                if self.unresolved[reference] is True:
                    # The referenced path has already been visited and is still unresolved
                    # so we have a circular reference
                    raise CircularReference(value.url, path, reference)
            try:
                self.resolve_path(reference)
            except NoSuchPath:
                del self.unresolved[reference]
                raise NoSuchReference(value.url, path, reference)
        try:
            value = value.resolve(self.parameters, self.inventory, self.environment)
        except InterpolationError as exception:
            exception.path = path + Path.fromlist(exception.reverse_path[::-1])
            raise
        except Exception as exception:
            raise InterpolateUnhandledError(exception, url=value.url, path=path, value=value)
        if value.unresolved:
            self.visit_count[path] += 1
            if self.visit_count[path] > 255:
                # this path has been revisited an excessive number of times there is probably
                # an error somewhere
                raise ExcessivePathRevisits(value.url, path)
        return value
