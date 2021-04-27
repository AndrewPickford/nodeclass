import os
from collections import defaultdict
from .exceptions import ClassNotFoundError, DuplicateClassError, DuplicateNodeError, NodeNotFoundError

class FileSystem:
    '''
    '''

    def __init__(self, basedir, file_format):
        self.basedir = os.path.abspath(basedir)
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
        return f'{self.__class__.__name__}({self.basedir})'


class FileSystemClasses(FileSystem):
    def __init__(self, basedir, file_format):
        super().__init__(basedir, file_format)

    def __getitem__(self, classname):
        path = self.classname_to_path(classname)
        try:
            return FileSystem.__getitem__(self, path), path
        except FileNotFoundError as exc:
            raise ClassNotFoundError(classname, [path])

    def classname_to_path(self, classname):
        base = classname.replace('.', '/')
        basepaths = [ f'{base}', f'{base}/init' ]
        paths = [ f'{path}.{ext}' for ext in self.format.extensions for path in basepaths ]
        present = [ path for path in paths if path in self ]
        if len(present) == 1:
            return present[0]
        elif len(present) > 1:
            raise DuplicateClassError(classname, duplicates=present)
        raise ClassNotFoundError(classname, paths)


class FileSystemNodes(FileSystem):
    '''
    '''

    def __init__(self, basedir, file_format):
        super().__init__(basedir, file_format)
        self.nodes = self.node_list(basepath=basedir)

    def __getitem__(self, nodename):
        if nodename not in self.nodes:
            raise NodeNotFoundError(nodename)
        elif len(self.nodes[nodename]) != 1:
            raise DuplicateNodeError(nodename, duplicates=self.nodes[nodename])
        try:
            path = self.nodes[nodename][0]
            return FileSystem.__getitem__(self, path), path
        except FileNotFoundError as exc:
            raise NodeNotFoundError(nodename, path)

    def node_list(self, basepath):
        nodes = defaultdict(list)
        for (dirpath, dirnames, filenames) in os.walk(self.basedir):
            for file in filenames:
                path = os.path.join(dirpath, file)
                nodename, extension = os.path.splitext(file)
                if extension[1:] in self.format.extensions:
                    nodes[nodename].append(os.path.relpath(path, start=basepath))
        return nodes
