from reclass.utils import Path
from reclass.value import value
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
        self.parameters = value({}, '')
        for i, k in enumerate(klasses):
            d = value(k, str(i))
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
        if self.unresolved[path]:
            # this path has been visited before so we are in a circular reference
            raise InteroplationInfiniteRecursionError(path)
        self.unresolved[path] = True

        val = self.parameters[path]
        if val.unresolved():
            for r in val.references():
                if r in self.unresolved:
                    self.resolve_path(r)
            val = val.resolve(self.parameters, self.inventory)
        self.parameters[path] = val

        if val.unresolved():
            # there is an additional level of indirection and this path must be
            # revisited
            self.unresolved[path] = False
            self.visit_count[path] = self.visit_count.get(path, 0) + 1
            if self.visit_count[path] > 255:
                # this path has been revisited an excessive number of times there is probably
                # an error somewhere
                raise InteroplationExcessiveRevisitsError(path)
        else:
            del self.unresolved[path]
        return
