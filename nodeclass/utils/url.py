from abc import ABC, abstractmethod

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any

class Url(ABC):
    def __init__(self, name: 'str'):
        self.name = name

    @abstractmethod
    def __eq__(self, other: 'Any') -> 'bool':
        pass

    @abstractmethod
    def __str__(self) -> 'str':
        pass


class EmptyUrl(Url):
    def __init__(self):
        super().__init__('')

    def __eq__(self, other: 'Any') -> 'bool':
        if self.__class__ != other.__class__:
            return False
        return True

    def __str__(self) -> 'str':
        return 'No url set'


class PseudoUrl(Url):
    def __init__(self, name: 'str', location: 'str'):
        super().__init__(name)
        self.location = location

    def __eq__(self, other: 'Any') -> 'bool':
        if self.__class__ != other.__class__:
            return False
        if self.location == other.location:
            return True
        return False

    def __str__(self) -> 'str':
        return self.location


class FileUrl(Url):
    def __init__(self, name: 'str', resource: 'str', path: 'str'):
        super().__init__(name)
        self.resource = resource
        self.path = path

    def __eq__(self, other: 'Any') -> 'bool':
        if self.__class__ != other.__class__:
            return False
        if self.resource == other.resource and self.path == other.path:
            return True
        return False

    def __str__(self) -> 'str':
        return '{0}:{1}'.format(self.resource, self.path)


class GitUrl(Url):
    def __init__(self, name: 'str', resource: 'str', repo: 'str', branch: 'str', path: 'str'):
        super().__init__(name)
        self.resource = resource
        self.repo = repo
        self.branch = branch
        self.path = path

    def __eq__(self, other: 'Any') -> 'bool':
        if self.__class__ != other.__class__:
            return False
        if self.resource == other.resource and self.repo == other.repo and \
           self.branch == other.branch and self.path == other.path:
            return True
        return False

    def __str__(self) -> 'str':
        return '{0}:{1} {2} {3}'.format(self.resource, self.repo, self.branch, self.path)
