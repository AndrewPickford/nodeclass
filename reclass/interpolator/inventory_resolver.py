import copy
from collections import defaultdict
from ..exceptions import ProcessError
from .exceptions import ExcessivePathRevisits

class InventoryResolver:
    '''
    '''

    def __init__(self, parameter_resolver):
        self.parameter_resolver = parameter_resolver

    def resolve(self, exports, parameters, paths):
        '''
        exports: Dictionary of merged exports
        parameters: Dictionary of merged parameters
        paths: set of paths in the exports to resolve
        returns: Dictionary of resolved exports
        '''
        self.exports = copy.copy(exports)
        self.parameters = copy.copy(parameters)
        self.parameter_resolver.environment = None
        self.parameter_resolver.inventory = None
        self.parameter_resolver.parameters = self.parameters
        self.parameter_resolver.visit_count = defaultdict(int)
        self.parameter_resolver.unresolved = None
        self.unresolved = dict.fromkeys(paths, False)
        self.visit_count = defaultdict(int)
        try:
            self.resolve_unresolved_paths()
        except ProcessError as exception:
            exception.hierarchy_type = 'inventory'
            raise
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
            value = self.exports[path]
            while value.unresolved:
                value = self.resolve_value(path, value)
            new_paths = value.unresolved_paths(path)
            if new_paths:
                self.unresolved.update(dict.fromkeys(new_paths, False))
            self.exports[path] = value
        del self.unresolved[path]
        return

    def resolve_value(self, path, value):
        if value.references:
            self.parameter_resolver.unresolved = dict.fromkeys(value.references, False)
            self.parameter_resolver.resolve_unresolved_paths()
        value = value.resolve(self.parameters, None, None)
        if value.unresolved:
            self.visit_count[path] += 1
            if self.visit_count[path] > 255:
                # this path has been revisited an excessive number of times there is probably
                # an error somewhere
                raise ExcessivePathRevisits(value.url, path)
        return value
