"""File-level recovery for explicitly selected documentation experiment trees.

Capture before mutation, seal after generation, then restore. A sealed inventory
is an ownership assertion by the operator, not automatic proof of authorship.
Conflicting edits abort before restoration; backups remain available afterward.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile


def checked(path):
    path = Path(os.path.abspath(path))
    for part in [*reversed(path.parents), path]:
        if part.is_symlink():
            raise ValueError(f'Symlink rejected: {part}')
    return path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inventory(root):
    checked(root)
    if not root.exists():
        return {}
    if not root.is_dir():
        raise ValueError(f'Not a directory: {root}')
    result = {'.': {'mode': stat.S_IMODE(root.stat().st_mode), 'kind': 'directory'}}
    for path in sorted(root.rglob('*')):
        checked(path)
        item = {'mode': stat.S_IMODE(path.stat().st_mode)}
        if path.is_file():
            item.update(kind='file', sha256=digest(path.read_bytes()))
        elif path.is_dir():
            item['kind'] = 'directory'
        else:
            raise ValueError(f'Special file rejected: {path}')
        result[str(path.relative_to(root))] = item
    return result


def atomic(path, data, mode=0o600):
    checked(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.recovery-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save(session, record):
    atomic(session / 'manifest.json', (json.dumps(record, indent=2) + '\n').encode())


def capture(session, roots):
    session = checked(session)
    roots = [checked(root) for root in roots]
    if not roots or len(set(roots)) != len(roots):
        raise ValueError('Select distinct documentation roots')
    for root in roots:
        if root == session or root in session.parents or session in root.parents:
            raise ValueError('Recovery directory overlaps documentation')
        if any(other != root and other in root.parents for other in roots):
            raise ValueError('Documentation roots overlap')
    snapshots = [inventory(root) for root in roots]
    session.mkdir(mode=0o700, parents=True, exist_ok=False)
    record = {'schema': 1, 'status': 'capturing', 'trees': []}
    for index, (root, before) in enumerate(zip(roots, snapshots)):
        for name, item in before.items():
            if item['kind'] == 'file':
                data = (root / name).read_bytes()
                if digest(data) != item['sha256']:
                    raise ValueError('Source changed during capture')
                atomic(session / 'originals' / str(index) / name, data, item['mode'])
        if inventory(root) != before:
            raise ValueError('Tree changed during capture')
        record['trees'].append({'root': str(root), 'before': before})
    record['status'] = 'captured'
    save(session, record)
    return record


def load(session):
    checked(session)
    checked(session / 'manifest.json')
    record = json.loads((session / 'manifest.json').read_text())
    if record.get('schema') != 1:
        raise ValueError('Unsupported manifest')
    return record


def seal(session):
    record = load(session)
    if record['status'] != 'captured':
        raise ValueError('Only a captured session can be sealed')
    for tree in record['trees']:
        tree['after'] = inventory(Path(tree['root']))
    record['status'] = 'sealed'
    save(session, record)
    return record


def restore(session):
    record = load(session)
    if record['status'] not in {'sealed', 'restoring', 'restored'}:
        raise ValueError('Seal ownership before restoration')
    # Preflight every tree and backup before the first mutation. Both states are
    # allowed, making a retry safe after an interruption between file operations.
    for index, tree in enumerate(record['trees']):
        current = inventory(Path(tree['root']))
        before, after = tree['before'], tree['after']
        for name in current.keys() | before.keys() | after.keys():
            if current.get(name) not in (before.get(name), after.get(name)):
                raise ValueError(f'Ownership conflict: {tree["root"]}/{name}')
        for name, item in before.items():
            if item['kind'] == 'file':
                backup = checked(session / 'originals' / str(index) / name)
                if not backup.is_file() or digest(backup.read_bytes()) != item['sha256']:
                    raise ValueError(f'Corrupt recovery bytes: {name}')
        for name in before.keys() & after.keys():
            if before[name]['kind'] != after[name]['kind']:
                raise ValueError('File/directory replacement needs manual recovery')
    record['status'] = 'restoring'
    save(session, record)
    for index, tree in enumerate(record['trees']):
        root = checked(tree['root'])
        before = tree['before']
        for name, item in sorted(before.items(), key=lambda pair: len(Path(pair[0]).parts)):
            path = checked(root / name)
            if item['kind'] == 'directory':
                path.mkdir(parents=True, exist_ok=True)
            else:
                atomic(path, (session / 'originals' / str(index) / name).read_bytes(), item['mode'])
        for name, item in sorted(tree['after'].items(), key=lambda pair: len(Path(pair[0]).parts), reverse=True):
            if name not in before:
                path = checked(root / name)
                if path.exists():
                    path.rmdir() if item['kind'] == 'directory' else path.unlink()
        for name, item in before.items():
            os.chmod(root / name, item['mode'])
        if inventory(root) != before:
            raise ValueError(f'Restoration verification failed: {root}')
    record['status'] = 'restored'
    save(session, record)
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['capture', 'seal', 'restore'])
    parser.add_argument('--session', required=True, type=Path)
    parser.add_argument('--root', action='append', default=[], type=Path)
    args = parser.parse_args()
    result = capture(args.session, args.root) if args.operation == 'capture' else globals()[args.operation](args.session)
    print(json.dumps({'status': result['status'], 'trees': len(result['trees'])}))
