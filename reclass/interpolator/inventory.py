import copy
from reclass.utils.path import Path

class Inventory:
    def __init__(self, settings):
        self.settings = copy.copy(settings)
        self.Path = type('XPath', (Path, ), { 'delimiter': settings.delimiter })

    def interpolate(self, queries, nodes_loader, klasses_loader):
        references = set()
        exports = set()
        for query in queries:
            references.update({self.Path.fromstring(ref) for ref in query.references})
            exports.update({self.Path.fromstring(exp) for exp in query.exports})
        print(references)
        print(exports)
