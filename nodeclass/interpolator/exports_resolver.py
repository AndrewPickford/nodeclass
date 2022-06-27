import copy
from collections import defaultdict
from ..exceptions import InterpolationError
from ..value.exceptions import NoSuchPath
from .exceptions import ExcessivePathRevisits, MergableInterpolationError, MultipleInterpolationErrors, NoSuchReference

class ExportsResolver:
    '''
    '''

    def resolve(self, exports, parameters):
        '''
        exports: Dictionary of already merged exports to resolve
        parameters: Dictionary of resolved parameters
        returns: Dictionary of resolved exports
        '''
        self.parameters = parameters
        self.exports = copy.copy(exports)
        self.visit_count = defaultdict(int)
        self.unresolved = dict.fromkeys(self.exports.unresolved_paths(), False)
        self.interpolation_exceptions = {}
        self.resolve_unresolved_paths()
        if len(self.interpolation_exceptions) > 0:
            raise MultipleInterpolationErrors(list(self.interpolation_exceptions.values()))
        return self.exports

    def resolve_unresolved_paths(self):
        while len(self.unresolved) > 0:
            path = next(iter(self.unresolved))
            try:
                self.resolve_path(path)
            except MergableInterpolationError as exception:
                if exception.path in self.interpolation_exceptions:
                    raise MultipleInterpolationErrors(list(self.interpolation_exceptions.values()))
                else:
                    exception.category = 'exports'
                    self.interpolation_exceptions[path] = exception
                    del self.unresolved[path]
            except InterpolationError as exception:
                exception.category = 'exports'
                raise
        return

    def resolve_path(self, path):
        visit_count = 0
        while self.exports[path].unresolved:
            try:
                value = self.exports[path].resolve(self.parameters, None, None)
            except NoSuchPath as exception:
                raise NoSuchReference(self.exports[path].url, path, exception.missing_path)
            new_paths = value.unresolved_paths(path)
            if new_paths:
                self.unresolved.update(dict.fromkeys(new_paths, False))
            self.exports[path] = value
            if visit_count > 255:
                # this path has been revisited an excessive number of times there is probably
                # an error somewhere
                raise ExcessivePathRevisits(value.url, path)
            visit_count += 1
        del self.unresolved[path]
        return
