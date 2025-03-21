import collections
import os
from packaging.version import Version
from typing import NamedTuple
from ..utils.holdlock import HoldLock
from ..utils.misc import ensure_directory_present
from ..utils.url import GitUrl
from .exceptions import BadNodeBranch, ClassNotFound, DuplicateClass, DuplicateNode, FileParsingError, InvalidUriOption, NodeNotFound, NoMatchingBranch, PygitConfigError, RequiredUriOptionMissing

try:
    # NOTE: in some distros pygit2 could require special effort to acquire.
    # It is not a problem per se, but it breaks tests for no real reason.
    # This try block is for keeping tests sane.
    import pygit2
except ImportError:
    pygit2 = None

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Generator, List, Optional, Tuple, Union
    from ..settings import ConfigDict
    from .factory import StorageCache
    from .format import Format


class GitFileMetaData(NamedTuple):
    name: 'str'
    path: 'str'
    id: 'str'


class NoSuchBranch(Exception):
    def __init__(self, branch):
        self.branch = branch


class GitRepo:
    '''
    '''

    ignored_options = [ 'resource', 'branch', 'path' ]
    required_options = [ 'repo' ]
    valid_options = [ 'cache_dir', 'lock_dir', 'pubkey', 'privkey', 'password' ] + required_options

    @classmethod
    def validate_uri(cls, uri: 'ConfigDict') -> 'ConfigDict':
        def validate_option(option: 'str') -> 'str':
            if option not in cls.valid_options:
                raise InvalidUriOption(uri, option)
            return option

        options = { validate_option(option): value for option, value in uri.items() if option not in cls.ignored_options }
        for required in cls.required_options:
            if required not in options:
                raise RequiredUriOptionMissing(uri, required)
        return options

    @classmethod
    def uri_from_string(cls, uri_string: 'str') -> 'ConfigDict':
        resource, repo = uri_string.split(':', 1)
        return { 'resource': resource, 'repo': repo }

    @classmethod
    def from_uri(cls, uri: 'ConfigDict', cache: 'Optional[StorageCache]') -> 'GitRepo':
        uri_valid = cls.validate_uri(uri)
        if cache is None:
            return cls(**uri_valid)
        name = 'git_repo {0}'.format(uri['repo'])
        if name not in cache:
            cache[name] = cls(**uri_valid)
        return cache[name]

    def __init__(self, repo: 'str', cache_dir: 'Optional[str]' = None, lock_dir: 'Optional[str]' = None, pubkey: 'Optional[str]' = None, privkey: 'Optional[str]' = None, password: 'Optional[str]' = None):
        self._check_pygit2()
        self.transport, self.remote = repo.split('://', 1)
        self.id = self.remote.replace('/', '_')
        if cache_dir:
            self.cache_dir = '{0}/{1}'.format(cache_dir, self.id)
        else:
            self.cache_dir = '{0}/{1}/{2}'.format(os.path.expanduser("~"), '.nodeclass/cache/git', self.id)
        if lock_dir:
            self.lock_file = '{0}/{1}'.format(lock_dir, self.id)
        else:
            self.lock_file = '{0}/{1}/{2}'.format(os.path.expanduser("~"), '.nodeclass/cache/lock', self.id)
        ensure_directory_present(os.path.dirname(self.lock_file))
        self.remotecallbacks = self._setup_remotecallbacks(pubkey, privkey, password)
        with HoldLock(self.lock_file):
            self._initialise()
            self._fetch()
        self.branches = self.repo.listall_branches()

    def _check_pygit2(self):
        if pygit2 is None:
            raise PygitConfigError('No pygit2 module')
        if Version(pygit2.__version__) < Version('0.26.4'):
            raise PygitConfigError('Require version 0.26.4 of pygit2 or higher')

    def _initialise(self):
        if os.path.exists(self.cache_dir):
            self.repo = pygit2.Repository(self.cache_dir)
        else:
            os.makedirs(self.cache_dir)
            self.repo = pygit2.init_repository(self.cache_dir, bare=True)
            self.repo.remotes.create('origin', self.remote)

    def _setup_remotecallbacks(self, pubkey: 'Optional[str]', privkey: 'Optional[str]', password: 'Optional[str]') -> 'Union[pygit2.RemoteCallbacks, None]':
        if 'ssh' in self.transport:
            if '@' in self.remote:
                user, _ = self.remote.split('@', 1)
            else:
                user = 'gitlab'

            if pubkey is None:
                credentials = pygit2.KeypairFromAgent(user)
            else:
                credentials = pygit2.Keypair(user, pubkey, privkey, password)

            remotecallbacks = pygit2.RemoteCallbacks(credentials=credentials)
            return remotecallbacks
        return None

    def _fetch(self):
        origin = self.repo.remotes['origin']
        fetch_kwargs = {}
        if self.remotecallbacks is not None:
            fetch_kwargs['callbacks'] = self.remotecallbacks
        origin.fetch(**fetch_kwargs)
        remote_branches = self.repo.listall_branches(pygit2.GIT_BRANCH_REMOTE)
        local_branches = self.repo.listall_branches()
        for remote_branch_name in remote_branches:
            _, _, local_branch_name = remote_branch_name.partition('/')
            remote_branch = self.repo.lookup_branch(remote_branch_name, pygit2.GIT_BRANCH_REMOTE)
            if local_branch_name not in local_branches:
                local_branch = self.repo.create_branch(local_branch_name, self.repo[remote_branch.target.hex])
                local_branch.upstream = remote_branch
            else:
                local_branch = self.repo.lookup_branch(local_branch_name)
                if local_branch.target != remote_branch.target:
                    local_branch.set_target(remote_branch.target)

        local_branches = self.repo.listall_branches()
        for local_branch_name in local_branches:
            remote_branch_name = '{0}/{1}'.format(origin.name, local_branch_name)
            if remote_branch_name not in remote_branches:
                local_branch = self.repo.lookup_branch(local_branch_name)
                local_branch.delete()

    def _files_in_tree(self, tree: 'pygit2.Tree', path: 'str') -> 'Generator[GitFileMetaData, None, None]':
        for entry in tree:
            if entry.filemode == pygit2.GIT_FILEMODE_TREE:
                subtree = self.repo.get(entry.id)
                if path == '':
                    subpath = entry.name
                else:
                    subpath = '/'.join([path, entry.name])
                yield from self._files_in_tree(subtree, subpath)
            else:
                if path == '':
                   relpath = entry.name
                else:
                   relpath = '/'.join([path, entry.name])
                yield GitFileMetaData(entry.name, relpath, entry.id)

    def get(self, id: 'str') -> 'pygit2.Commit':
        return self.repo.get(id)

    def files_in_branch(self, branch: 'str') -> 'Generator[GitFileMetaData, None, None]':
        try:
            tree = self.repo.revparse_single(branch).tree
        except KeyError:
            raise NoSuchBranch(branch)
        return self._files_in_tree(tree, '')


class GitRepoClasses:
    '''
    '''

    valid_options = GitRepo.ignored_options + GitRepo.valid_options

    @classmethod
    def clean_uri(cls, uri: 'ConfigDict') -> 'ConfigDict':
        return { k: v for k, v in uri.items() if k in cls.valid_options }

    @classmethod
    def subpath(cls, uri_str: 'str') -> 'ConfigDict':
        uri = cls.uri_from_string(uri_str)
        uri['path'] = 'classes'
        return uri

    @classmethod
    def uri_from_string(cls, uri_str: 'str') -> 'ConfigDict':
        return GitRepo.uri_from_string(uri_str)

    def __init__(self, classes_uri: 'ConfigDict', format: 'Format', cache: 'Optional[StorageCache]' = None):
        self.git_repo = GitRepo.from_uri(classes_uri, cache)
        self.repo = classes_uri['repo']
        self.resource = classes_uri['resource']
        self.branch = classes_uri.get('branch', None) or 'master'
        self.path = classes_uri.get('path', None)
        self.format = format
        self.index_map: Dict[str, Dict[str, GitFileMetaData]] = {}
        if self.branch != '__env__':
            self.index_map[self.branch] = self._make_index(self.branch)

    def __str__(self) -> 'str':
        return '{0}:{1}'.format(self.resource, self.repo)

    def _make_index(self, branch: 'str') -> 'Dict[str, GitFileMetaData]':
        index: 'Dict[str, GitFileMetaData]' = {}
        try:
            files = self.git_repo.files_in_branch(branch)
        except NoSuchBranch:
            raise NoMatchingBranch(branch, self.repo)
        for file in files:
            name = self.format.mangle_name(file.name)
            if name:
                index[file.path] = file
        return index

    def _name_to_meta(self, name: 'str', index: 'Dict[str, GitFileMetaData]') -> 'GitFileMetaData':
        base = name.replace('.', '/')
        if self.path:
            base = os.path.join(self.path, base)
        paths = self.format.possible_class_paths(base)
        present = [ path for path in paths if path in index ]
        if len(present) == 1:
            return index[present[0]]
        elif len(present) > 1:
            duplicates = [ self._path_url(name, duplicate) for duplicate in present ]
            raise DuplicateClass(name, duplicates)
        raise ClassNotFound(name, [ self._path_url(name, path) for path in paths ])

    def _path_url(self, name: 'str', path: 'str') -> 'GitUrl':
        return GitUrl(name, self.resource, self.repo, self.branch, path)

    def get(self, name: 'str', environment: 'str') -> 'Tuple[Dict, GitUrl]':
        if self.branch == '__env__':
            if environment not in self.index_map:
                self.index_map[environment] = self._make_index(environment)
            index = self.index_map[environment]
        else:
            index = self.index_map[self.branch]
        meta = self._name_to_meta(name, index)
        blob = self.git_repo.get(meta.id)
        try:
           blob_data = self.format.process(blob.data)
           path_url = self._path_url(name, meta.path)
        except FileParsingError as exception:
            exception.url = self._path_url(name, meta.path)
        return blob_data, path_url


class GitRepoNodes:
    '''
    '''

    @classmethod
    def subpath(cls, uri_str: 'str') -> 'ConfigDict':
        uri = cls.uri_from_string(uri_str)
        uri['path'] = 'nodes'
        return uri

    @classmethod
    def uri_from_string(cls, uri_str: 'str') -> 'ConfigDict':
        return GitRepo.uri_from_string(uri_str)

    def __init__(self, nodes_uri: 'ConfigDict', format: 'Format', cache: 'Optional[StorageCache]'=None):
        self.git_repo = GitRepo.from_uri(nodes_uri, cache)
        self.repo = nodes_uri['repo']
        self.resource = nodes_uri['resource']
        self.branch = nodes_uri.get('branch', None) or 'master'
        self.path = nodes_uri.get('path', None)
        self.format = format
        self.node_map = self._make_node_map()

    def __str__(self) -> 'str':
        return '{0}:{1}'.format(self.resource, self.repo)

    def _make_node_map(self) -> 'Dict[str, List[GitFileMetaData]]':
        node_map = collections.defaultdict(list)
        try:
            files = self.git_repo.files_in_branch(self.branch)
        except NoSuchBranch:
            raise BadNodeBranch(self.branch)
        for file in files:
            if self.path is None or file.path.startswith(self.path):
                name = self.format.mangle_name(file.name)
                if name:
                    node_map[name].append(file)
        return node_map

    def _path_url(self, name: 'str', path: 'str') -> 'GitUrl':
        return GitUrl(name, self.resource, self.repo, self.branch, path)

    def get(self, name: 'str') -> 'Tuple[Dict, GitUrl]':
        if name not in self.node_map:
            raise NodeNotFound(name, '{0} branch {1}'.format(self.repo, self.branch))
        elif len(self.node_map[name]) != 1:
            duplicates = [ self._path_url(name, duplicate.path) for duplicate in self.node_map[name] ]
            raise DuplicateNode(name, str(self), duplicates)
        meta = self.node_map[name][0]
        blob = self.git_repo.get(meta.id)
        try:
            blob_data = self.format.process(blob.data)
            path_url = self._path_url(name, meta.path)
        except FileParsingError as exception:
            exception.url = self._path_url(name, meta.path)
        return blob_data, path_url
