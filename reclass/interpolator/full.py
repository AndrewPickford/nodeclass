from collections import defaultdict
from copy import copy
from reclass.item.parser import Parser
from reclass.value.factory import ValueFactory
from .exceptions import InterpolationExcessiveRevisitsError, InterpolationCircularReferenceError

class Full:
    '''
    '''

    def __init__(self, settings):
        self.settings = copy(settings)
        self.parser = Parser(self.settings)
        self.Path = self.parser.Path
        self.value_factory = ValueFactory(self.settings, self.parser, self.parser.Scalar)

    def interpolate(self, classes, inventory):
        self.inventory = inventory
        self.parameters = self.merge(classes)
        self.unresolved = dict.fromkeys(self.parameters.unresolved_paths(self.Path.empty()), False)
        self.visit_count = defaultdict(int)
        self.resolve()
        return self.parameters.render_all()

    def merge(self, classes):
        parameters = self.value_factory.make_value_dictionary({}, '')
        for klass in classes:
            vd = self.value_factory.make_value_dictionary(klass.parameters, klass.url)
            parameters.merge(vd)
        return parameters

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
        val, new_paths = val.resolve(self.parameters, self.inventory)
        if new_paths:
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
