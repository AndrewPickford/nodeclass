import os
from collections import defaultdict
from .exceptions import ClassNotFoundError, DuplicateClassError, DuplicateNodeError, NodeNotFoundError

class FileSystem:
    '''
    '''

    def __init__(self, path, file_format):
        self.basedir = os.path.abspath(path)
        self.format = file_format

    def __contains__(self, path):
        fullpath = os.path.join(self.basedir, path)
        return os.path.exists(fullpath)

    def __getitem__(self, path):
        fullpath = os.path.join(self.basedir, path)
        if self.format.load:
            return self.format.load(fullpath)
        else:
            with open(fullpath) as file:
                return self.format.process(file.read())

    def __repr__(self):
        return '{0}({1}_fs{2})'.format(self.__class__.__name__, self.format.name, self.basedir)

    def __str__(self):
        return '{0}_fs:{1}'.format(self.format.name, self.basedir)

    def url(self, path):
        return '{0}_fs:{1}'.format(self.format.name, os.path.join(self.basedir, path))


class FileSystemClasses(FileSystem):
    def __init__(self, path, file_format):
        super().__init__(path, file_format)

    def __getitem__(self, classname):
        path = self.classname_to_path(classname)
        try:
            return FileSystem.__getitem__(self, path), path
        except FileNotFoundError as exc:
            raise ClassNotFoundError(classname, [ self.url(path) ])

    def classname_to_path(self, classname):
        base = classname.replace('.', '/')
        basepaths = [ '{0}'.format(base), '{0}/init'.format(base) ]
        paths = [ '{0}.{1}'.format(path, ext) for ext in self.format.extensions for path in basepaths ]
        present = [ path for path in paths if path in self ]
        if len(present) == 1:
            return present[0]
        elif len(present) > 1:
            duplicates = [ self.url(duplicate) for duplicate in present ]
            raise DuplicateClassError(classname, duplicates)
        raise ClassNotFoundError(classname, [ self.url(path) for path in paths ])


class FileSystemNodes(FileSystem):
    '''
    '''

    def __init__(self, path, file_format):
        super().__init__(path, file_format)
        self.nodes = self.node_list()

    def __getitem__(self, nodename):
        if nodename not in self.nodes:
            raise NodeNotFoundError(nodename, str(self))
        elif len(self.nodes[nodename]) != 1:
            duplicates = [ self.url(duplicate) for duplicate in self.nodes[nodename] ]
            raise DuplicateNodeError(nodename, str(self), duplicates)
        try:
            path = self.nodes[nodename][0]
            return FileSystem.__getitem__(self, path), path
        except FileNotFoundError as exc:
            raise NodeNotFoundError(nodename, str(self))

    def node_list(self):
        nodes = defaultdict(list)
        for (dirpath, dirnames, filenames) in os.walk(self.basedir):
            for file in filenames:
                path = os.path.join(dirpath, file)
                nodename, extension = os.path.splitext(file)
                if extension[1:] in self.format.extensions:
                    nodes[nodename].append(os.path.relpath(path, start=self.basedir))
        return nodes
