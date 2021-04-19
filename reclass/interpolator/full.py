from reclass.utils import Path
from reclass.value import value
from .exceptions import InteroplationInfiniteRecursionError

class Full:
    '''
    '''

    def interpolate(self, klasses, inventory):
        self.inventory = inventory
        self.merge(klasses)
        self.initialise()
        self.resolve()
        return self.parameters.render()

    def merge(self, klasses):
        self.parameters = value({}, '')
        for i, k in enumerate(klasses):
            d = value(k, str(i))
            self.parameters.merge(d)
        return

    def initialise(self):
        self.unresolved = dict.fromkeys(self.parameters.unresolved_paths(Path.Empty()), False)
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
        for r in val.references():
            if r in self.unresolved:
                self.resolve_path(r)
        val = val.resolve(self.parameters, self.inventory)
        self.parameters[path] = val
        if not val.unresolved():
            del self.unresolved[path]
        return
