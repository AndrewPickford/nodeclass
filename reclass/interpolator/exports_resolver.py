import copy
from collections import defaultdict
from reclass.utils.path import Path as BasePath
from .exceptions import InterpolationExcessiveRevisitsError

class ExportsResolver:
    '''
    '''
    Path = BasePath

    def resolve(self, exports, parameters):
        '''
        exports: Dictionary of already merged exports to resolve
        parameters: Dictionary of resolved parameters
        returns: Dictionary of resolved exports
        '''
        self.parameters = parameters
        self.exports = copy.copy(exports)
        self.visit_count = defaultdict(int)
        self.unresolved = dict.fromkeys(self.exports.unresolved_paths(self.Path.empty()), False)
        self.resolve_unresolved_paths()
        self.visit_count = None
        return self.exports

    def resolve_unresolved_paths(self):
        while len(self.unresolved) > 0:
            path = next(iter(self.unresolved))
            self.resolve_path(path)
        return

    def resolve_path(self, path):
        visit_count = 0
        while self.exports[path].unresolved:
            self.exports[path] = self.exports[path].resolve(self.parameters, None, None)
            if visit_count > 255:
                # this path has been revisited an excessive number of times there is probably
                # an error somewhere
                raise InterpolationExcessiveRevisitsError(path)
            visit_count += 1
        del self.unresolved[path]
        return
