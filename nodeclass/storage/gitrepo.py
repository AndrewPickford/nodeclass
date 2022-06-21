import collections
import distutils.version
import os
from ..utils.holdlock import HoldLock
from ..utils.misc import ensure_directory_present
from .exceptions import ClassNotFound, DuplicateClass, DuplicateNode, FileParsingError, InvalidUri, NodeNotFound, PygitConfigError

try:
    # NOTE: in some distros pygit2 could require special effort to acquire.
    # It is not a problem per se, but it breaks tests for no real reason.
    # This try block is for keeping tests sane.
    import pygit2
except ImportError:
    pygit2 = None


GitFileMetaData = collections.namedtuple('GitFileMetaData', ['name', 'path', 'id'], rename=False)


class GitRepo:
    '''
    '''

    ignored_options = [ 'resource', 'branch', 'path' ]
    required_options = [ 'repo' ]
    valid_options = [ 'cache_dir', 'lock_dir', 'pubkey', 'privkey', 'password' ] + required_options

    @classmethod
    def validate_uri(cls, uri):
        def validate_option(option):
            if option not in cls.valid_options:
                raise InvalidUri(uri, 'Invalid uri option {0}'.format(option))
            return option

        options = { validate_option(option): value for option, value in uri.items() if option not in cls.ignored_options }
        for required in cls.required_options:
            if required not in options:
                raise InvalidUri(uri, 'Required option not present: {0}'.format(required))
        return options

    @classmethod
    def uri_from_string(cls, uri_string):
        resource, repo = uri_string.split(':', 1)
        return { 'resource': resource, 'repo': repo }

    @classmethod
    def from_uri(cls, uri, cache):
        if isinstance(uri, str):
            uri = cls.uri_from_string(uri)
        uri_valid = cls.validate_uri(uri)
        if cache is None:
            return cls(**uri_valid), uri
        name = 'git_repo {0}'.format(uri['repo'])
        if name not in cache:
            cache[name] = cls(**uri_valid)
        return cache[name], uri

    def __init__(self, repo, cache_dir=None, lock_dir=None, pubkey=None, privkey=None, password=None):
        self._check_pygit2()
        self.transport, self.url = repo.split('://', 1)
        self.id = self.url.replace('/', '_')
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
            raise PygitConfigError('No pygit module')
        pygit2_version = pygit2.__version__
        if distutils.version.LooseVersion(pygit2_version) < distutils.version.LooseVersion('0.23.2'):
            raise PygitConfigError('Require version 0.23.2 of pygit or higher')

    def _initialise(self):
        if os.path.exists(self.cache_dir):
            self.repo = pygit2.Repository(self.cache_dir)
        else:
            os.makedirs(self.cache_dir)
            self.repo = pygit2.init_repository(self.cache_dir, bare=True)
            self.repo.create_remote('origin', self.url)

    def _setup_remotecallbacks(self, pubkey, privkey, password):
        if 'ssh' in self.transport:
            if '@' in self.url:
                user, _ = self.url.split('@', 1)
            else:
                user = 'gitlab'

            if pubkey is None:
                credentials = pygit2.KeypairFromAgent(user)
            else:
                credentials = pygit2.Keypair(user, pubkey, privkey, password)

            pygit2_version = pygit2.__version__
            if distutils.version.LooseVersion(pygit2_version) < distutils.version.LooseVersion('0.23.2'):
                raise PygitConfigError('Require version 0.23.2 of pygit or higher')

            remotecallbacks = pygit2.RemoteCallbacks(credentials=credentials)
            return remotecallbacks
        return None

    def _fetch(self):
        origin = self.repo.remotes[0]
        fetch_kwargs = {}
        if self.remotecallbacks is not None:
            fetch_kwargs['callbacks'] = self.remotecallbacks
        fetch_results = origin.fetch(**fetch_kwargs)
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

    def _files_in_tree(self, tree, path):
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

    def get(self, id):
        return self.repo.get(id)

    def files_in_branch(self, branch):
        tree = self.repo.revparse_single(branch).tree
        return self._files_in_tree(tree, '')


class GitRepoClasses:
    '''
    '''

    valid_options = GitRepo.ignored_options + GitRepo.valid_options

    @classmethod
    def clean_uri(cls, uri):
        return { k: v for k, v in uri.items() if k in cls.valid_options }

    @classmethod
    def subpath(cls, uri):
        if isinstance(uri, str):
            uri = GitRepo.uri_from_string(uri)
        uri['path'] = 'classes'
        return uri

    def __init__(self, uri, format, cache=None):
        self.git_repo, uri = GitRepo.from_uri(uri, cache)
        self.repo = uri['repo']
        self.resource = uri['resource']
        self.branch = uri.get('branch', None) or 'master'
        self.path = uri.get('path', None)
        self.format = format
        self.index_map = {}
        if self.branch != '__env__':
            self.index_map[self.branch] = self._make_index(self.branch)

    def _make_index(self, branch):
        index = {}
        for file in self.git_repo.files_in_branch(branch):
            name = self.format.mangle_name(file.name)
            if name:
                index[file.path] = file
        return index

    def _name_to_meta(self, name, index):
        base = name.replace('.', '/')
        if self.path:
            base = os.path.join(self.path, base)
        paths = self.format.possible_class_paths(base)
        present = [ path for path in paths if path in index ]
        if len(present) == 1:
            return index[present[0]]
        elif len(present) > 1:
            duplicates = [ self._path_url(duplicate) for duplicate in present ]
            raise DuplicateClass(name, duplicates)
        raise ClassNotFound(name, [ self._path_url(path) for path in paths ])

    def _path_url(self, path):
        return '{0}:{1} {2} {3}'.format(self.resource, self.repo, self.branch, path)

    def get(self, name, environment):
        if self.branch == '__env__':
            if environment not in self.index_map:
                self.index_map[environment] = self._make_index(environment)
            index = self.index_map[environment]
        else:
            index = self.index_map[self.branch]
        meta = self._name_to_meta(name, index)
        blob = self.git_repo.get(meta.id)
        try:
           return self.format.process(blob.data), self._path_url(meta.path)
        except FileParsingError as exception:
            exception.url = self._path_url(meta.path)

class GitRepoNodes:
    '''
    '''

    @classmethod
    def subpath(cls, uri):
        if isinstance(uri, str):
            uri = GitRepo.uri_from_string(uri)
        uri['path'] = 'nodes'
        return uri

    def __init__(self, uri, format, cache=None):
        self.git_repo, uri = GitRepo.from_uri(uri, cache)
        self.repo = uri['repo']
        self.resource = uri['resource']
        self.branch = uri.get('branch', None) or 'master'
        self.path = uri.get('path', None)
        self.format = format
        self.node_map = self._make_node_map()

    def _make_node_map(self):
        node_map = collections.defaultdict(list)
        for file in self.git_repo.files_in_branch(self.branch):
            if self.path is None or file.path.startswith(self.path):
                name = self.format.mangle_name(file.name)
                if name:
                    node_map[name].append(file)
        return node_map

    def _path_url(self, path):
        return '{0}:{1} {2} {3}'.format(self.resource, self.repo, self.branch, path)

    def get(self, name):
        if name not in self.node_map:
            raise NodeNotFound(name, str(self))
        elif len(self.node_map[name]) != 1:
            duplicates = [ self._path_url(duplicate) for duplicate in self.node_map[name] ]
            raise DuplicateNode(name, str(self), duplicates)
        meta = self.node_map[name][0]
        blob = self.git_repo.get(meta.id)
        try:
            return self.format.process(blob.data), self._path_url(meta.path)
        except FileParsingError as exception:
            exception.url = self._path_url(meta.path)
