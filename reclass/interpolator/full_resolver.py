import copy
from collections import defaultdict
from reclass.item.parser import Parser
from reclass.value.factory import ValueFactory
from .exceptions import InterpolationExcessiveRevisitsError, InterpolationCircularReferenceError

class FullResolver:
    '''
    '''

    def __init__(self, path_class):
        self.Path = path_class

    def resolve_parameters(self, parameters, inventory):
        '''
        parameters: Dictionary of already merged parameters to resolve
        inventory: Dictionary of pre-evaluated inventory query answers
        returns: Dictionary of resolved parameters
        '''
        self.parameters = parameters
        self.inventory = inventory
        self.unresolved = dict.fromkeys(self.parameters.unresolved_paths(self.Path.empty()), False)
        self.visit_count = defaultdict(int)
        while len(self.unresolved) > 0:
            path = next(iter(self.unresolved))
            self.resolve_path(path)
        return self.parameters

    def resolve_exports(self, exports, parameters):
        '''
        exports: Dictionary of already merged exports to resolve
        parameters: Dictionary of resolved parameters
        returns: Dictionary of resolved exports
        '''
        self.parameters = parameters
        self.exports = exports
        self.unresolved = dict.fromkeys(self.exports.unresolved_paths(self.Path.empty()), False)
        self.visit_count = defaultdict(int)
        while len(self.unresolved) > 0:
            path = next(iter(self.unresolved))
            self.resolve_export(path)
        return self.exports

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
        del self.unresolved[path]
        return

    def resolve_value(self, path):
        '''
        Remove one level of indirection, adding any new reference paths required to
        self.unresolved

        If this method needs to be called a second time for a given path keep a count
        of the number of times this method has been called for the path and raise an
        error if the visit count threshold is exceeded.
        '''
        val = self.parameters[path]
        for reference in val.references:
            if self.parameters.unresolved_ancestor(reference):
                self.resolve_path(reference.parent())
            if reference in self.unresolved:
                if self.unresolved[reference] == True:
                    # The referenced path has already been visited and is still unresolved
                    # so we have a circular reference
                    raise InterpolationCircularReferenceError(path, reference)
                self.resolve_path(reference)
        val, check_new_paths = val.resolve(self.parameters, self.inventory)
        if check_new_paths:
            new_paths = dict.fromkeys(val.unresolved_paths(path))
            if len(new_paths) > 0:
                self.unresolved.update(dict.fromkeys(val.unresolved_paths(path), False))
        self.parameters[path] = val

        if val.unresolved:
            # a nested reference or a Merged value following a chain of references
            self.visit_count[path] += 1
            if self.visit_count[path] > 255:
                # this path has been revisited an excessive number of times there is probably
                # an error somewhere
                raise InterpolationExcessiveRevisitsError(path)
            self.resolve_value(path)
        return

    def resolve_export(self, path):
        val = self.exports[path]
        if val.unresolved:
            val, new_paths = val.resolve(self.parameters, None)
            if new_paths:
                self.unresolved.update(dict.fromkeys(val.unresolved_paths(path), False))
            self.visit_count[path] += 1
            self.exports[path] = val
            if self.visit_count[path] > 255:
                # this path has been revisited an excessive number of times there is probably
                # an error somewhere
                raise InterpolationExcessiveRevisitsError(path)
        else:
            del self.unresolved[path]
        return
