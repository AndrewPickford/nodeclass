import copy
from collections import defaultdict
from ..exceptions import InterpolationError
from ..utils.path import Path
from ..value.exceptions import NoSuchPath
from .exceptions import ExcessivePathRevisits, CircularReference, InterpolateUnhandledError, NoSuchReference

class ParametersResolver:
    '''
    '''

    def resolve(self, environment, parameters, inventory):
        '''
        environment: Environment to resolve the parameters in
        parameters: Dictionary of already merged parameters to resolve
        inventory: Dictionary of pre-evaluated inventory query answers
        returns: Dictionary of resolved parameters
        '''
        self.environment = environment
        self.parameters = copy.copy(parameters)
        self.inventory = inventory
        self.visit_count = defaultdict(int)
        self.unresolved = dict.fromkeys(self.parameters.unresolved_paths(), False)
        try:
            self.resolve_unresolved_paths()
        except InterpolationError as exception:
            exception.hierarchy_type = 'parameters'
            raise
        return self.parameters

    def resolve_unresolved_paths(self):
        while len(self.unresolved) > 0:
            path = next(iter(self.unresolved))
            self.resolve_path(path)
        return

    def resolve_path(self, path):
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

    def resolve_value(self, path, value):
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
