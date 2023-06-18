import copy
from collections import defaultdict
from ..exceptions import ProcessError
from ..value.exceptions import NoSuchPath
from .exceptions import ExcessivePathRevisits, InterpolateUnhandledError, InventoryQueryError, NoSuchReference

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict
    from ..utils.path import Path
    from .exceptions import MergableInterpolationError

class InventoryResolver:
    '''
    '''

    def __init__(self, parameter_resolver):
        self.parameter_resolver = parameter_resolver

    def resolve(self, exports, parameters, queries):
        '''
        exports: Dictionary of merged exports
        parameters: Dictionary of merged parameters
        paths: set of paths in the exports to resolve
        returns: Dictionary of resolved exports
        '''
        self.exports = copy.copy(exports)
        self.parameters = copy.copy(parameters)
        self.parameter_resolver.environment = None
        self.parameter_resolver.parameters = self.parameters
        self.parameter_resolver.inventory = None
        self.parameter_resolver.visit_count = defaultdict(int)
        self.parameter_resolver.unresolved = None
        self.parameter_resolver.interpolation_exceptions: 'Dict[Path, MergableInterpolationError]' = {}
        for query in queries:
            try:
                self.resolve_query(query)
            except ProcessError as exception:
                raise InventoryQueryError(query, exception)
        return self.exports

    def resolve_query(self, query):
        self.unresolved = dict.fromkeys(query.exports, False)
        self.visit_count = defaultdict(int)
        self.resolve_unresolved_paths()
        return

    def resolve_unresolved_paths(self):
        while len(self.unresolved) > 0:
            path = next(iter(self.unresolved))
            self.resolve_path(path)
        return

    def resolve_path(self, path):
        try:
            if self.exports.unresolved_ancestor(path):
                self.unresolved[path.parent()] = False
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
        except ProcessError:
            raise
        except Exception as exception:
            try:
                value = self.exports.get(path, None)
                url = value.url
            except Exception:
                value = None
                url = None
            raise InterpolateUnhandledError(exception, url=url, path=path, value=value)

    def resolve_value(self, path, value):
        if value.references:
            self.parameter_resolver.unresolved = dict.fromkeys(value.references, False)
            try:
                self.parameter_resolver.resolve_unresolved_paths()
            except NoSuchPath as exception:
                raise NoSuchReference(value.url, path, exception.missing_path, category='exports')
        value = value.resolve(self.parameters, None, None)
        if value.unresolved:
            self.visit_count[path] += 1
            if self.visit_count[path] > 255:
                # this path has been revisited an excessive number of times there is probably
                # an error somewhere
                raise ExcessivePathRevisits(value.url, path, category='exports')
        return value
