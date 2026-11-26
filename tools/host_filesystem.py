import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys
import threading
import signal
import time

LIBRARY = Path(__file__).resolve().parent.parent
# Reuse the campaign's descriptor-based, no-follow filesystem primitive.
spec = importlib.util.spec_from_file_location('workspace', LIBRARY / 'agent/tools/documentation_workspace.py')
ws = importlib.util.module_from_spec(spec)
bytecode_setting = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    spec.loader.exec_module(ws)
finally:
    sys.dont_write_bytecode = bytecode_setting
EXTENSIONS = set('.rb .py .js .ts .tsx .jsx .go .rs .php .java .kt .swift .sh .sql .toml .mod .yaml .yml .c .h .cc .hh .cpp .hpp .cxx .hxx .cs .gd'.split())
EXCLUDED = set('.git .aws .codex .agents node_modules vendor target dist build coverage tmp log logs storage public docs docs_codex test tests spec fixtures .next .dockerized-postgres ollama skills agent'.split())
MANIFESTS = {'Gemfile', 'package.json', 'Cargo.toml', 'go.mod', 'composer.json', 'requirements.txt', 'pyproject.toml'}
DOC_TARGETS = {'en/guides/generated-source-summary.md', 'pt-br/guides/generated-source-summary.md', 'en/index.md', 'pt-br/index.md'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def document_value(entries, relative, root):
    if relative in entries:
        return entries[relative]
    # On a case-insensitive host, pt-BR and pt-br can be the same file.
    # Require filesystem identity; do not merge distinct paths on Linux.
    matches = []
    for name, value in entries.items():
        if name.casefold() != relative.casefold():
            continue
        try:
            if os.path.samefile(root / relative, root / name):
                matches.append(value)
        except FileNotFoundError:
            continue
    if len(matches) > 1:
        raise ValueError('ambiguous documentation aliases')
    return matches[0] if matches else None


def atomic(path, data):
    path = Path(path)
    with ws.directory(path.parent) as fd:
        temporary = 'exchange-' + secrets.token_hex(16)
        ws.write_new(fd, temporary, data)
        try:
            if path.is_symlink():
                raise ValueError('linked exchange file')
            os.replace(temporary, path.name, src_dir_fd=fd, dst_dir_fd=fd)
            os.fsync(fd)
        finally:
            try:
                os.unlink(temporary, dir_fd=fd)
            except FileNotFoundError:
                pass


def json_write(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False).encode())


def mkdir(path):
    path = Path(path)
    if not path.exists():
        mkdir(path.parent)
        path.mkdir(mode=0o700)
    with ws.directory(path):
        pass
    return path


class HostFilesystem:
    def __init__(self, library, exchange):
        self.library = Path(library).absolute()
        self.exchange = mkdir(Path(exchange).absolute())
        def limit(name, default, maximum):
            value = int(os.environ.get(name, default))
            if not 1 <= value <= maximum:
                raise ValueError(name + ' outside bounded configuration')
            return value
        self.file_bytes = limit('DOCS_HOST_FILE_BYTES', 32 * 1024 * 1024, 128 * 1024 * 1024)
        self.source_bytes = limit('DOCS_HOST_SOURCE_BYTES', 512 * 1024 * 1024, 8 * 1024 * 1024 * 1024)
        self.docs_bytes = limit('DOCS_HOST_DOCS_BYTES', 128 * 1024 * 1024, 1024 * 1024 * 1024)
        self.entry_limit = limit('DOCS_HOST_ENTRIES', 200000, 2000000)
        self.file_limit = limit('DOCS_HOST_FILES', 100000, 200000)

        for name in ('requests', 'responses', 'workspaces'):
            mkdir(self.exchange / name)

    def resolve(self, reference):
        if not isinstance(reference, str) or not reference or len(reference.encode()) > 4096 or re.search(r'[\x00-\x1f\x7f]', reference):
            raise ValueError('invalid relative project reference')
        reference = reference.replace('\\', '/')
        if reference.startswith('/') or re.match(r'^[A-Za-z]:', reference):
            raise ValueError('absolute project reference rejected')
        path = Path(os.path.abspath(self.library / reference))
        # Opening every directory by descriptor rejects symlinks including ancestors.
        with ws.directory(path):
            pass
        canonical = Path(path.anchor)
        for part in path.parts[1:]:
            with ws.directory(canonical) as fd:
                names = os.listdir(fd)
                if part not in names:
                    expected = os.stat(part, dir_fd=fd, follow_symlinks=False)
                    matches = [name for name in names if (lambda st: (st.st_dev, st.st_ino) == (expected.st_dev, expected.st_ino))(os.stat(name, dir_fd=fd, follow_symlinks=False))]
                    if len(matches) != 1:
                        raise ValueError('ambiguous project spelling')
                    part = matches[0]
            canonical /= part
        path = canonical
        if not (path / '.git').is_dir() or (path / '.git').is_symlink():
            raise ValueError('a standalone Git project is required')
        with ws.directory(path / '.git'):
            pass
        if (path / '.git/objects/info/alternates').exists():
            raise ValueError('external Git object storage rejected')
        return path

    def identity(self, source):
        env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_OPTIONAL_LOCKS='0', GIT_NO_LAZY_FETCH='1', GIT_NO_REPLACE_OBJECTS='1', GIT_TERMINAL_PROMPT='0')
        result = subprocess.run(['git', '--no-optional-locks', '-c', 'core.hooksPath=' + os.devnull,
                                 '-c', 'core.fsmonitor=false', '-c', 'safe.directory=' + str(source),
                                 '-C', str(source), 'rev-list', '--max-parents=0', 'HEAD'],
                                env=env, capture_output=True, timeout=20, check=True)
        roots = result.stdout.decode().split()
        if not roots or not all(re.fullmatch('[0-9a-f]{40,64}', x) for x in roots):
            raise ValueError('Git identity unavailable')
        return digest('\n'.join(sorted(roots)).encode())

    def inspect(self, request):
        source = self.resolve(request['reference'])
        fingerprint = self.identity(source)
        if request.get('identity') and request['identity'] != fingerprint:
            raise ValueError('project identity changed')
        return {'identity': fingerprint, 'name': source.name}

    def same_source(self, request):
        candidate = self.resolve(request['otherReference'])
        if self.identity(candidate) != request['identity']:
            raise ValueError('project identity changed')
        try:
            previous = self.resolve(request['reference'])
        except FileNotFoundError:
            return {'same': False}
        return {'same': os.path.samefile(previous, candidate)}

    def missing(self, request):
        reference = request['reference']
        # Resolve the accessible parent; do not infer absence from a missing share.
        if not isinstance(reference, str) or not reference or len(reference.encode()) > 4096 or re.search(r'[\x00-\x1f\x7f]', reference):
            raise ValueError('invalid relative reference')
        normalized = reference.replace('\\', '/')
        if normalized.startswith('/') or re.match(r'^[A-Za-z]:', normalized):
            raise ValueError('relative reference required')
        path = Path(os.path.abspath(self.library / normalized))
        with ws.directory(path.parent) as fd:
            names = os.listdir(fd)
            import unicodedata
            canonical = lambda s: unicodedata.normalize('NFC', s).casefold()
            absent = not any(canonical(n) == canonical(path.name) for n in names)
        return {'missing': absent}

    def copy_source(self, staged, relative, data):
        target = staged / relative
        mkdir(target.parent)
        try:
            with ws.directory(staged) as fd:
                existing, _ = ws.read(fd, relative, self.file_bytes)
            if digest(existing) == digest(data):
                return False
        except FileNotFoundError:
            pass
        atomic(target, data)
        return True

    def source_files(self, source, staged=None):
        files = {}
        total = 0
        visited = 0
        copied = 0
        def walk(fd, prefix='', depth=0):
            nonlocal total, visited, copied
            if depth > 32:
                raise ValueError('source depth exceeds bound')
            for name in sorted(os.listdir(fd)):
                visited += 1
                if visited > self.entry_limit:
                    raise ValueError('source inventory exceeds bound')
                if name.lower() in EXCLUDED or name.startswith('.') or re.search(r'secret|credential|private.?key|password|token|service.account|(?:\.spec|\.test|_test)\.', name, re.I):
                    continue
                info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                relative = prefix + name
                if stat.S_ISDIR(info.st_mode):
                    child = os.open(name, ws.directory_flags(), dir_fd=fd)
                    try:
                        if '.git' not in os.listdir(child):
                            walk(child, relative + '/', depth + 1)
                    finally:
                        os.close(child)
                elif stat.S_ISREG(info.st_mode) and (Path(name).suffix in EXTENSIONS or name in MANIFESTS):
                    data, _ = ws.read(fd, name, self.file_bytes)
                    total += len(data)
                    if total > self.source_bytes or len(files) >= self.file_limit:
                        raise ValueError('source snapshot exceeds DOCS_HOST_SOURCE_BYTES or DOCS_HOST_FILES; no acquisition was accepted')
                    files[relative] = digest(data)
                    if staged is not None:
                        copied += self.copy_source(staged, relative, data)

        with ws.directory(source) as fd:
            walk(fd)
        self.acquisition = {'candidateFiles': len(files), 'bytes': total, 'copiedFiles': copied, 'completeInventory': True}
        return files

    def docs(self, source):
        result = {}
        total = 0
        if not (source / 'docs').exists() and not (source / 'docs').is_symlink():
            return result
        visited = 0
        def walk(fd, prefix='', depth=0):
            nonlocal total, visited
            if depth > 32:
                raise ValueError('documentation depth exceeds bound')
            for name in sorted(os.listdir(fd)):
                visited += 1
                if visited > self.entry_limit:
                    raise ValueError('documentation inventory exceeds DOCS_HOST_ENTRIES')
                if name.startswith('.'):
                    continue
                info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                relative = prefix + name
                if stat.S_ISDIR(info.st_mode):
                    child = os.open(name, ws.directory_flags(), dir_fd=fd)
                    try:
                        walk(child, relative + '/', depth + 1)
                    finally:
                        os.close(child)
                elif stat.S_ISREG(info.st_mode) and Path(name).suffix.lower() == '.md':
                    data, _ = ws.read(fd, name, self.file_bytes)
                    total += len(data)
                    if total > self.docs_bytes:
                        raise ValueError('documentation snapshot exceeds DOCS_HOST_DOCS_BYTES')
                    result[relative] = data
                elif not stat.S_ISREG(info.st_mode):
                    raise ValueError('linked or special documentation entry rejected')
        with ws.directory(source / 'docs') as fd:
            walk(fd)
        return result

    def prepare(self, request):
        info = self.inspect(request)
        source = self.resolve(request['reference'])
        if source == self.library:
            raise ValueError('the library itself must retain its existing self-documentation mapping')
        key = digest(request['reference'].encode())
        home = mkdir(self.exchange / 'workspaces' / key)
        metadata = home / 'snapshot.json'
        if metadata.exists():
            with ws.directory(home) as fd:
                previous = json.loads(ws.read(fd, 'snapshot.json', 32 * 1024 * 1024)[0])
            if previous['name'] != source.name or previous['identity'] != info['identity'] or previous['reference'] != request['reference']:
                raise ValueError('snapshot identity or reference changed; recovery required')
            staged_docs = home / previous['name'] / 'docs'
            changed = False
            with ws.directory(staged_docs) as fd:
                for relative in DOC_TARGETS:
                    try:
                        data, _ = ws.read(fd, relative, 2_097_152)
                    except FileNotFoundError:
                        continue
                    changed |= digest(data) != document_value(previous['docHashes'], relative, staged_docs)
            if previous.get('pending') or changed:
                return {'key': key, **info}
        root_stat = source.stat()
        staged = mkdir(home / source.name)
        files = self.source_files(source, staged)
        docs = self.docs(source)
        if (source.stat().st_dev, source.stat().st_ino) != (root_stat.st_dev, root_stat.st_ino):
            raise ValueError('project relocated during preparation')
        # Fixed workspace location keeps MakeDocs ownership paths stable across restarts.
        staged = mkdir(home / source.name)
        old = previous if metadata.exists() else {}
        for relative in old.get('sourceHashes', {}):
            if relative not in files:
                with ws.directory(staged) as fd:
                    with ws.parent(fd, relative) as (parent, leaf):
                        os.unlink(leaf, dir_fd=parent)
        mkdir(staged / 'docs')
        for relative in old.get('docHashes', {}):
            if relative not in docs:
                with ws.directory(staged / 'docs') as fd:
                    with ws.parent(fd, relative) as (parent, leaf):
                        try:
                            os.unlink(leaf, dir_fd=parent)
                        except FileNotFoundError:
                            pass
        for relative, data in docs.items():
            self.copy_source(staged / 'docs', relative, data)
        # Never erase a staged publication after an interrupted delivery.
        doc_hashes = {p: digest(b) for p, b in docs.items()}
        record = {'reference': request['reference'], **info, 'sourceHashes': files, 'acquisition': self.acquisition, 'docHashes': doc_hashes, 'rootIdentity': [root_stat.st_dev, root_stat.st_ino], 'pending': False}
        encoded = json.dumps(record, ensure_ascii=False).encode()
        if len(encoded) > 32 * 1024 * 1024:
            raise ValueError('snapshot inventory exceeds 32 MiB; no acquisition was accepted')
        atomic(metadata, encoded)
        return {'key': key, **info, 'acquisition': self.acquisition}

    def publish(self, request):
        key = request['key']
        if not re.fullmatch('[0-9a-f]{64}', key):
            raise ValueError('invalid workspace')
        home = self.exchange / 'workspaces' / key
        with ws.directory(home) as fd:
            record = json.loads(ws.read(fd, 'snapshot.json', 32 * 1024 * 1024)[0])
        source = self.resolve(record['reference'])
        if digest(record['reference'].encode()) != key or record['name'] != source.name:
            raise ValueError('snapshot reference or destination changed')
        root_stat = source.stat()
        if [root_stat.st_dev, root_stat.st_ino] != record['rootIdentity']:
            raise ValueError('project directory replaced since preparation')
        if self.identity(source) != record['identity']:
            raise ValueError('project identity changed before delivery')
        current = self.source_files(source)
        if current != record['sourceHashes']:
            raise ValueError('host sources changed during generation')
        staged = home / record['name'] / 'docs'
        changes = {}
        with ws.directory(staged) as fd:
            for relative in DOC_TARGETS:
                try:
                    data, _ = ws.read(fd, relative, 2_097_152)
                except FileNotFoundError:
                    continue
                if digest(data) != document_value(record['docHashes'], relative, staged):
                    changes[relative] = data
        # Preflight the entire delivery, then retain its journal until all writes finish.
        current_docs = self.docs(source)
        for relative, data in changes.items():
            current_data = document_value(current_docs, relative, source / 'docs')
            actual = digest(current_data) if current_data is not None else None
            if actual not in (document_value(record['docHashes'], relative, staged), digest(data)):
                raise ValueError('manual documentation edit; delivery refused')
        record['pending'] = True
        json_write(home / 'snapshot.json', record)
        destination = mkdir(source / 'docs')
        with ws.directory(destination) as fd:
            for relative, data in changes.items():
                current_root = source.stat()
                if [current_root.st_dev, current_root.st_ino] != record['rootIdentity'] or not ws.same_root(destination, fd):
                    raise ValueError('project documentation directory changed during delivery')
                with ws.parent(fd, relative, create=True) as (parent, leaf):
                    try:
                        before, _ = ws.read(fd, relative, 2_097_152)
                        actual = digest(before)
                    except FileNotFoundError:
                        actual = None
                    if actual not in (document_value(record['docHashes'], relative, staged), digest(data)):
                        raise ValueError('documentation changed during delivery')
                    if actual == digest(data):
                        continue
                    temporary = 'makedocs-' + secrets.token_hex(16)
                    ws.write_new(parent, temporary, data)
                    os.replace(temporary, leaf, src_dir_fd=parent, dst_dir_fd=parent)
                    os.fsync(parent)
        record['docHashes'].update({p: digest(b) for p, b in changes.items()})
        record['pending'] = False
        json_write(home / 'snapshot.json', record)
        return {'written': sorted(changes)}

    def serve(self):
        import fcntl
        with ws.directory(self.exchange) as fd:
            lock = os.open('worker.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        stop = threading.Event()
        signal.signal(signal.SIGTERM, lambda *_: stop.set())
        signal.signal(signal.SIGINT, lambda *_: stop.set())
        def heartbeat():
            while not stop.is_set():
                json_write(self.exchange / 'ready.json', {'at': time.time(), 'pid': os.getpid(), 'uid': os.getuid()})
                stop.wait(1)
        monitor = threading.Thread(target=heartbeat, daemon=True)
        monitor.start()
        print('Host filesystem adapter ready', flush=True)
        try:
            while not stop.is_set():
                for path in sorted((self.exchange / 'requests').glob('*.json')):
                    if not re.fullmatch(r'[0-9a-f]{32}\.json', path.name):
                        continue
                    try:
                        with ws.directory(path.parent) as fd:
                            request = json.loads(ws.read(fd, path.name, 16384)[0])
                        operation = request.pop('operation')
                        if operation not in ('inspect', 'missing', 'prepare', 'publish', 'same_source'):
                            raise ValueError('operation rejected')
                        result = {'result': getattr(self, operation)(request)}
                    except Exception as error:
                        result = {'error': type(error).__name__ + ': ' + str(error)}
                    json_write(self.exchange / 'responses' / path.name, result)
                    path.unlink()
                stop.wait(.1)
        finally:
            stop.set()
            monitor.join(timeout=3)
            self.exchange.joinpath('ready.json').unlink(missing_ok=True)
            os.close(lock)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--library', type=Path, default=LIBRARY)
    parser.add_argument('--exchange', type=Path)
    args = parser.parse_args()
    if Path('/.dockerenv').exists():
        parser.error('run the filesystem adapter on the host, never inside Docker')
    if os.name != 'posix':
        parser.error('descriptor-based access requires a POSIX host; on Windows run this adapter inside WSL2')
    exchange = args.exchange or args.library / 'backend/storage/makedocs/filesystem/host'
    HostFilesystem(args.library, exchange).serve()
