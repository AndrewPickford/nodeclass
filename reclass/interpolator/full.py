from reclass.utils import Path
from reclass.value import Value
from .exceptions import InteroplationExcessiveRevisitsError, InteroplationInfiniteRecursionError

class Full:
    '''
    '''

    def interpolate(self, klasses, inventory):
        self.inventory = inventory
        self.merge(klasses)
        self.initialise()
        self.resolve()
        return self.parameters.render_all()

    def merge(self, klasses):
        self.parameters = Value.Create({}, '')
        for k in klasses:
            d = Value.Create(k.parameters, k.uri)
            self.parameters.merge(d)
        return

    def initialise(self):
        self.unresolved = dict.fromkeys(self.parameters.unresolved_paths(Path.Empty()), False)
        self.visit_count = {}
        return

    def resolve(self):
        while len(self.unresolved) > 0:
            path = next(iter(self.unresolved))
            self.resolve_path(path)
        return

    def resolve_path(self, path):
        '''
        Dereference and/or merge the Value at the given path, by repeatedly calling
        resolve_value until:
            the Value resolves
            we revisit this path and hence have circular references
            the visit count for this path is exceeded
        '''
        if self.unresolved[path]:
            # this path has been visited before so we are in a circular reference
            raise InteroplationInfiniteRecursionError(path)
        self.unresolved[path] = True

        while self.parameters[path].unresolved():
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
        for r in val.references():
            if r in self.unresolved:
                self.resolve_path(r)
        val, new_paths = val.resolve(self.parameters, self.inventory)
        if new_paths:
            self.unresolved.update(dict.fromkeys(val.unresolved_paths(path), False))
        self.parameters[path] = val

        if val.unresolved():
            # a nested reference or a Merged value following a chain of references
            self.visit_count[path] = self.visit_count.get(path, 0) + 1
            if self.visit_count[path] > 255:
                # this path has been revisited an excessive number of times there is probably
                # an error somewhere
                raise InteroplationExcessiveRevisitsError(path)
            self.resolve_value(path)
        return
