#!/usr/bin/env python3
"""Cold, one-file bootstrap A. No Controller imports or phase/state writes.

The OLD runtime does not enforce this bootstrap marker. Cold single-author/no
launcher admission must be verified externally before actual use. This is NOT
bundle installation B, Game sync, Production Readiness or phase approval.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid

from bootstrap_runtime_fence import LEGACY_SHA, sha

BOOTSTRAP_SHA = 'd1c347d43877f79c276e606fcd55f2f6c58b62aace8ba4904d32fa2bd31585d5'
RUNNER = 'autopilot/runner.py'
MARKER = '.autopilot/BOOTSTRAP_PENDING.json'
B_MARKER = '.autopilot/HANDOFF_PENDING.json'
B_HISTORY = '.autopilot/RUNTIME_BUNDLE_STARTED.json'


class Refused(RuntimeError):
    pass


def checked(root, relative):
    p = Path(relative)
    if p.is_absolute() or not p.parts or any(x in ('.', '..') for x in p.parts):
        raise Refused('Unsafe relative path')
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            raise Refused('Symlink path: ' + relative)
    return current


def fingerprint(path):
    if path.is_symlink():
        raise Refused('Symlink file')
    try:
        s = path.stat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1:
        raise Refused('Expected single-link regular file: ' + str(path))
    return {'sha256': sha(path.read_bytes()), 'mode': stat.S_IMODE(s.st_mode),
            'uid': s.st_uid, 'gid': s.st_gid}


def syncdir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic(path, data, mode=0o600):
    tmp = path.parent / ('.' + path.name + '.' + uuid.uuid4().hex + '.tmp')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        syncdir(path.parent)
    finally:
        tmp.unlink(missing_ok=True)


def readjson(path):
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise Refused('Ambiguous JSON')
            d[k] = v
        return d
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def writejson(path, data):
    atomic(path, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


class Bootstrap:
    def __init__(self, root, hook=None):
        self.root = Path(root).absolute()
        if self.root.is_symlink() or self.root.resolve() != self.root or not checked(self.root, '.git').is_dir():
            raise Refused('Canonical checkout directory required')
        self.hook = hook or (lambda stage: None)
        self.fd = None

    @contextmanager
    def lease(self):
        lock = checked(self.root, 'automation/.executor.lock')
        old = lock.stat()
        self.fd = os.open(lock, os.O_RDWR | os.O_NOFOLLOW)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.identity = (old.st_dev, old.st_ino)
            self.check_lock()
            yield self
        finally:
            os.close(self.fd)
            self.fd = None

    def check_lock(self):
        if self.fd is None:
            raise Refused('Maintenance lease required')
        s = checked(self.root, 'automation/.executor.lock').stat()
        f = os.fstat(self.fd)
        if s.st_nlink != 1 or (s.st_dev, s.st_ino) != self.identity or (f.st_dev, f.st_ino) != self.identity:
            raise Refused('Lock inode changed')

    def protected(self, paths):
        return {p: fingerprint(checked(self.root, p)) for p in paths}

    def begin(self, candidate, protected_paths):
        self.check_lock()
        for name in (MARKER, B_MARKER, B_HISTORY):
            if checked(self.root, name).exists():
                raise Refused('Prior maintenance must be recovered independently')
        # Validate protected data before writing even backup metadata.
        protected = self.protected(protected_paths)
        runner = checked(self.root, RUNNER)
        before = fingerprint(runner)
        if before['sha256'] != LEGACY_SHA:
            raise Refused('Legacy source differs')
        if sha(candidate) != BOOTSTRAP_SHA:
            raise Refused('No reviewed candidate')
        if (before['uid'], before['gid']) != (os.geteuid(), os.getegid()):
            raise Refused('Ownership cannot be preserved by this user')
        # Actual use additionally requires independent exact-candidate GO.
        compile(candidate, RUNNER, 'exec')
        base = checked(self.root, '.autopilot')
        if not base.is_dir():
            raise Refused('Existing canonical .autopilot directory required')
        parent = checked(self.root, '.autopilot/bootstrap')
        if not parent.exists():
            parent.mkdir(mode=0o700)
            syncdir(base)
        folder = parent / uuid.uuid4().hex
        folder.mkdir(mode=0o700)
        syncdir(parent)
        old = runner.read_bytes()
        atomic(folder / 'old.py', old)
        atomic(folder / 'new.py', candidate)
        if sha((folder / 'old.py').read_bytes()) != before['sha256'] or sha((folder / 'new.py').read_bytes()) != sha(candidate):
            raise Refused('Backup verification failed')
        target = dict(before, sha256=sha(candidate))
        record = {'schema': 1, 'kind': 'BOOTSTRAP_A_NOT_BUNDLE', 'root': str(self.root),
                  'id': folder.name, 'before': before, 'target': target,
                  'protected': protected, 'lock': list(self.identity)}
        writejson(folder / 'intent.json', record)
        intent_sha = sha((folder / 'intent.json').read_bytes())
        writejson(folder / 'journal.json', {'id': folder.name, 'intent_sha256': intent_sha, 'status': 'PREPARED'})
        writejson(checked(self.root, MARKER), {'id': folder.name, 'intent_sha256': intent_sha})
        self.hook('prepared')
        return folder.name

    def load(self, ident):
        self.check_lock()
        if len(ident) != 32 or any(c not in '0123456789abcdef' for c in ident):
            raise Refused('Invalid transaction ID')
        folder = checked(self.root, '.autopilot/bootstrap/' + ident)
        relative = str(folder.relative_to(self.root))
        journal = readjson(checked(self.root, relative + '/journal.json'))
        intent = checked(self.root, relative + '/intent.json')
        intent_sha = sha(intent.read_bytes())
        if journal.get('intent_sha256') != intent_sha or journal.get('id') != ident:
            raise Refused('Immutable intent binding failed')
        if journal.get('status') not in ('PREPARED', 'VERIFIED', 'ROLLED_BACK'):
            raise Refused('Invalid journal outcome')
        record = readjson(intent)
        if 'status' in record or record.get('schema') != 1 or record.get('kind') != 'BOOTSTRAP_A_NOT_BUNDLE':
            raise Refused('Invalid immutable intent')
        record = dict(record, status=journal['status'])
        if record['root'] != str(self.root) or record['id'] != ident or record['lock'] != list(self.identity):
            raise Refused('Wrong maintenance identity')
        if any(checked(self.root, p).exists() for p in (B_MARKER, B_HISTORY)):
            raise Refused('B started: rollback A is forbidden')
        for name, expected in [('old.py', record['before']), ('new.py', record['target'])]:
            p = checked(self.root, str(folder.relative_to(self.root)) + '/' + name)
            if sha(p.read_bytes()) != expected['sha256']:
                raise Refused('Corrupt transaction bytes')
        if self.protected(record['protected']) != record['protected']:
            raise Refused('Protected data changed; do not restore stale state')
        if record['before']['sha256'] != LEGACY_SHA or record['target']['sha256'] != BOOTSTRAP_SHA:
            raise Refused('Unreviewed journal candidate')
        current = fingerprint(checked(self.root, RUNNER))
        if current not in (record['before'], record['target']):
            raise Refused('Unknown runner mutation')
        marker = checked(self.root, MARKER)
        if marker.exists():
            if readjson(marker) != {'id': ident, 'intent_sha256': intent_sha}:
                raise Refused('Another transaction or corrupt intent marker')
        elif record['status'] not in ('VERIFIED', 'ROLLED_BACK'):
            raise Refused('Missing maintenance intent')
        return folder, record

    def finish(self, ident, rollback=False):
        folder, record = self.load(ident)
        terminal = 'ROLLED_BACK' if rollback else 'VERIFIED'
        if record['status'] in ('VERIFIED', 'ROLLED_BACK') and record['status'] != terminal:
            raise Refused('Completed transaction cannot switch outcome')
        self.hook('before_replace')
        # A hook may emulate an interruption or independent file mutation.
        self.load(ident)
        target = record['before' if rollback else 'target']
        runner = checked(self.root, RUNNER)
        if fingerprint(runner) != target:
            data = (folder / ('old.py' if rollback else 'new.py')).read_bytes()
            atomic(runner, data, target['mode'])
        self.hook('after_replace')
        self.check_lock()
        if fingerprint(runner) != target or self.protected(record['protected']) != record['protected']:
            raise Refused('Post-replace verification failed')
        self.hook('before_commit')
        self.load(ident)
        if fingerprint(runner) != target or self.protected(record['protected']) != record['protected']:
            raise Refused('Commit inputs changed')
        record['status'] = terminal
        intent_sha = sha((folder / 'intent.json').read_bytes())
        writejson(folder / 'journal.json', {'id': ident, 'intent_sha256': intent_sha, 'status': terminal})
        self.hook('after_commit')
        # Commit and marker removal each require the original inode, immutable
        # ownership and protected-input checks, including idempotent recovery.
        self.load(ident)
        if fingerprint(runner) != target:
            raise Refused('Verified outcome changed before marker removal')
        marker = checked(self.root, MARKER)
        if marker.exists():
            if readjson(marker) != {'id': ident, 'intent_sha256': intent_sha}:
                raise Refused('Marker ownership changed')
            marker.unlink()
            syncdir(marker.parent)
        return record
