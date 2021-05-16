from ..exceptions import ReclassError

class ClassNotFoundError(ReclassError):
    def __init__(self, classname, urls):
        super().__init__()
        self.name = classname
        self.urls = urls
        self.environment = None

    @property
    def message(self):
        message = [ (0, 'No such class {0} in environment {1}, urls tried:'.format(self.name, self.environment)) ]
        message.extend([ (1, url) for url in self.urls ])
        return message


class DuplicateClassError(ReclassError):
    def __init__(self, classname, duplicates):
        super().__init__()
        self.name = classname
        self.duplicates = duplicates
        self.environment = None

    @property
    def message(self):
        message = [ (0, 'Duplicate definitions for class {0} in environment {1}:'.format(self.name, self.environment)) ]
        message.extend([ (1, url) for url in self.duplicates ])
        return message


class DuplicateNodeError(ReclassError):
    def __init__(self, classname, storage, duplicates):
        super().__init__()
        self.name = classname
        self.storage = storage
        self.duplicates = duplicates

    @property
    def message(self):
        message = [ (0, 'Duplicate node definitions for {0}:'.format(self.name, self.storage)) ]
        message.extend([ (1, url) for url in self.duplicates ])
        return message


class NodeNotFoundError(ReclassError):
    def __init__(self, nodename, storage):
        super().__init__()
        self.name = nodename
        self.storage = storage

    @property
    def message(self):
        message = [ (0, 'No such node {0} in storage {1}'.format(self.name, self.storage)) ]
        return message
