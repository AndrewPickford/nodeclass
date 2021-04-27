class ClassNotFoundError(Exception):
    def __init__(self, classname, paths):
        super().__init__()
        self.name = classname
        self.paths = paths


class DuplicateClassError(Exception):
    def __init__(self, classname, duplicates):
        super().__init__()
        self.name = classname
        self.duplicates = duplicates


class DuplicateNodeError(Exception):
    def __init__(self, classname, duplicates):
        super().__init__()
        self.name = classname
        self.duplicates = duplicates


class NodeNotFoundError(Exception):
    def __init__(self, nodename, path = None):
        super().__init__()
        self.name = nodename


class UnknownStorageTypeError(Exception):
    def __init__(self, storage_type, uri):
        super().__init__()
        self.storage_type = storage_type
        self.uri = uri
