import copy
from collections import defaultdict
from reclass.utils.path import Path as BasePath
from .exceptions import InterpolationExcessiveRevisitsError

class InventoryResolver:
    '''
    '''
    Path = BasePath

    def __init__(self, parameter_resolver):
        self.parameter_resolver = parameter_resolver

    def resolve(self, exports, parameters, paths):
        '''
        exports: Dictionary of merged exports
        parameters: Dictionary of merged parameters
        paths: set of paths in the exports to resolve
        returns: Dictionary of resolved exports
        '''
        self.parameters = copy.copy(parameters)
        self.exports = copy.copy(exports)
        self.parameter_resolver.environment = None
        self.parameter_resolver.inventory = None
        self.parameter_resolver.parameters = self.parameters
        self.parameter_resolver.visit_count = defaultdict(int)
        self.parameter_resolver.unresolved = dict.fromkeys(self.parameters.unresolved_paths(self.Path.empty()), False)
        self.unresolved = dict.fromkeys(paths, False)
        self.visit_count = defaultdict(int)
        self.resolve_unresolved_paths()
        self.visit_count = None
        self.parameter_resolver.visit_count = None
        return self.exports

    def resolve_unresolved_paths(self):
        while len(self.unresolved) > 0:
            path = next(iter(self.unresolved))
            self.resolve_path(path)
        return

    def resolve_path(self, path):
        if self.exports.unresolved_ancestor(path):
            self.resolve_path(path.parent())
        if path in self.exports:
            while self.exports[path].unresolved:
                self.resolve_value(path)
            new_paths = self.exports[path].unresolved_paths(path)
            self.unresolved.update(dict.fromkeys(new_paths, False))
        del self.unresolved[path]
        return

    def resolve_value(self, path):
        if self.exports[path].references:
            self.parameter_resolver.unresolved = dict.fromkeys(self.exports[path].references, False)
            self.parameter_resolver.resolve_unresolved_paths()
        self.exports[path] = self.exports[path].resolve(self.parameters, None, None)
        self.visit_count[path] += 1
        if self.visit_count[path] > 255:
            # this path has been revisited an excessive number of times there is probably
            # an error somewhere
            raise InterpolationExcessiveRevisitsError(path)
