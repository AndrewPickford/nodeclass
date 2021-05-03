import copy
from collections import defaultdict
from reclass.utils.path import Path as BasePath
from .exceptions import InterpolationExcessiveRevisitsError, InterpolationCircularReferenceError

class ParametersResolver:
    '''
    '''
    Path = BasePath

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
        self.unresolved = dict.fromkeys(self.parameters.unresolved_paths(self.Path.empty()), False)
        self.resolve_unresolved_paths()
        self.visit_count = None
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
        while self.parameters[path].unresolved:
            self.resolve_value(path)
        new_paths = self.parameters[path].unresolved_paths(path)
        if new_paths:
            self.unresolved.update(dict.fromkeys(new_paths, False))
        del self.unresolved[path]
        return

    def resolve_value(self, path):
        '''
        Remove one level of indirection

        If this method needs to be called a second time for a given path keep a count
        of the number of times this method has been called for the path and raise an
        error if the visit count threshold is exceeded.
        '''
        val = self.parameters[path]
        for reference in val.references:
            if reference in self.unresolved:
                if self.unresolved[reference] == True:
                    # The referenced path has already been visited and is still unresolved
                    # so we have a circular reference
                    raise InterpolationCircularReferenceError(path, reference)
            self.resolve_path(reference)
        val = val.resolve(self.parameters, self.inventory, self.environment)
        if val.unresolved:
            self.visit_count[path] += 1
            if self.visit_count[path] > 255:
                # this path has been revisited an excessive number of times there is probably
                # an error somewhere
                raise InterpolationExcessiveRevisitsError(path)
        self.parameters[path] = val
        return
