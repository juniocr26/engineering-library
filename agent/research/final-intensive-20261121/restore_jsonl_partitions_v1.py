"""Restore the three partitioned inventory streams as validated local artifacts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

REL = Path('agent/research/final-intensive-20261121')
VERSIONS = (2, 3, 4)


def checked_path(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('unsafe partition path')
    path = root / relative
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError('unsafe partition symlink or escaped path')
    return path


def identity(path, entry, blob=False):
    if not path.is_file() or path.stat().st_size != entry['bytes']:
        raise ValueError(f'missing file or size mismatch: {path}')
    digest = hashlib.sha256()
    git = hashlib.sha1(b'blob ' + str(entry['bytes']).encode() + b'\0')
    records = 0
    last = b''
    with path.open('rb') as stream:
        for line in stream:
            json.loads(line.decode('utf-8'))
            digest.update(line)
            git.update(line)
            records += 1
            last = line
    if digest.hexdigest() != entry['sha256'] or records != entry['records']:
        raise ValueError(f'checksum or record count mismatch: {path}')
    if blob and (entry['git_object_format'] != 'sha1'
                 or git.hexdigest() != entry['git_blob_oid']
                 or last.endswith(b'\n') != entry['ends_with_lf']
                 or (path.stat().st_mode & 0o777) != int(entry['mode'], 8)):
        raise ValueError(f'original identity mismatch: {path}')


def restore(root, destination=None):
    root = Path(root).resolve(strict=True)
    destination = root if destination is None else Path(destination).resolve(strict=True)
    folder = REL / 'jsonl-partitions-v1'
    restored = []
    for version in VERSIONS:
        stem = f'temporary-replay-file-inventory-records-v{version}'
        manifest = checked_path(root, folder / (stem + '.manifest.json'))
        data = json.loads(manifest.read_bytes())
        original = data['original']
        parts = data['partition']['parts']
        if (data['schema_version'] != 1 or original['path'] != str(REL / (stem + '.jsonl'))
                or not parts or data['partition']['max_part_bytes'] != 31457280
                or sum(p['bytes'] for p in parts) != original['bytes']
                or sum(p['records'] for p in parts) != original['records']):
            raise ValueError('invalid partition manifest')
        inputs = []
        for number, entry in enumerate(parts, 1):
            if (entry['sequence'] != number
                    or entry['file'] != f'{stem}.part-{number:04d}.jsonl'
                    or not 0 < entry['bytes'] <= 31457280):
                raise ValueError('invalid partition order or size')
            part = checked_path(root, folder / entry['file'])
            identity(part, entry)
            inputs.append(part)
        target = checked_path(destination, original['path'])
        if target.exists():
            identity(target, original, blob=True)
            restored.append({'path': original['path'], 'status': 'ALREADY_VALID'})
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix='.' + stem + '-', dir=target.parent)
        temporary = Path(temporary)
        try:
            with os.fdopen(fd, 'wb') as output:
                for part in inputs:
                    with part.open('rb') as stream:
                        for block in iter(lambda: stream.read(1024 * 1024), b''):
                            output.write(block)
                output.flush()
                os.fsync(output.fileno())
            temporary.chmod(int(original['mode'], 8))
            identity(temporary, original, blob=True)
            # Atomic publication refuses to overwrite a concurrently created file.
            os.link(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        restored.append({'path': original['path'], 'status': 'RESTORED'})
    return restored


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    print(json.dumps(restore(args.root, args.destination)))
