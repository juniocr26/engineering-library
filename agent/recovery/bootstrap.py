#!/usr/bin/env python3
"""Offline recovery: verify first, install into a new store, publish manifest last."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def load_manifest():
    path = Path(__file__).parent / 'manifest.json'
    raw = path.read_bytes()
    manifest = json.loads(raw)
    entries = {entry['path']: entry for entry in manifest['operational_files']}
    for supplement in sorted(path.parent.glob('makedocs-operational-*.json')):
        data = json.loads(supplement.read_text())
        if 'operational_files' not in data:
            continue
        if data.get('base_manifest_sha256') != hashlib.sha256(raw).hexdigest():
            raise ValueError('MakeDocs recovery supplement belongs to a different model lock')
        for entry in data['operational_files']:
            entries[entry['path']] = entry
    manifest['operational_files'] = list(entries.values())
    return manifest
SMALL_BLOB_LIMIT = 64 * 1024
SMALL_BLOB_MEDIA_TYPES = frozenset({
    'application/vnd.docker.container.image.v1+json',
    'application/vnd.docker.distribution.manifest.v2+json',
    'application/vnd.ollama.image.template',
    'application/vnd.ollama.image.params',
    'application/vnd.ollama.image.license',
})

# Reviewed minimum for recovery schema1; additions may be pinned in the lock.
REQUIRED_OPERATIONAL_FILES = frozenset({
    '.dockerignore',
    'agent/IDENTITY_NORMALIZATION.md',
    'agent/README.md',
    'agent/authoring.json',
    'agent/evaluation.json',
    'agent/experimental-session.en.md',
    'agent/experimental-session.pt-BR.md',
    'agent/instructions.en.md',
    'agent/instructions.pt-BR.md',
    'agent/recovery/bootstrap.py',
    'agent/recovery/bundle.py',
    'agent/recovery/model-bundle.json',
    'agent/skills/LICENSE.upstream',
    'agent/skills/authoring/SKILL.md',
    'agent/skills/evidence/SKILL.md',
    'agent/skills/provenance.json',
    'agent/skills/review/SKILL.md',
    'agent/sources.json',
    'backend/Gemfile',
    'backend/Gemfile.lock',
    'backend/Makefile',
    'backend/lib/documentation/command.rb',
    'backend/lib/documentation/native_structure.py',
    'backend/lib/documentation/project_command.rb',
    'backend/lib/documentation/python_structure.py',
    'backend/lib/documentation/research.rb',
    'compose.yaml',
    'docker/Dockerfile',
    'docker/backend-entrypoint.sh',
})


def contained(root, relative):
    if any(p.is_symlink() for p in [root, *root.parents]):
        raise ValueError('symlink store rejected')
    p = Path(relative)
    if p.is_absolute() or not p.parts or '..' in p.parts:
        raise ValueError('unsafe artifact path')
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('symlink artifact rejected')
    return current


def verify_file(path, entry):
    if not path.is_file() or path.stat().st_size != entry['size']:
        raise ValueError('missing artifact or size mismatch: ' + str(path))
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    if digest.hexdigest() != entry['sha256']:
        raise ValueError('checksum mismatch: ' + str(path))


def check_knowledge(manifest):
    if (not isinstance(manifest, dict)
            or type(manifest.get('schema_version')) is not int
            or manifest['schema_version'] != 1):
        raise ValueError('unsupported recovery schema')
    entries = manifest.get('operational_files')
    if not isinstance(entries, list) or not entries:
        raise ValueError('invalid operational file inventory')
    paths = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError('invalid operational file entry')
        value = entry.get('path')
        if not isinstance(value, str) or '\x00' in value or '\\' in value:
            raise ValueError('invalid operational file path')
        path = PurePosixPath(value)
        if (path.is_absolute() or not path.parts or '..' in path.parts
                or path.as_posix() != value):
            raise ValueError('unsafe operational file path')
        digest = entry.get('sha256')
        if (type(entry.get('size')) is not int or entry['size'] < 0
                or not isinstance(digest, str) or len(digest) != 64
                or any(char not in '0123456789abcdef' for char in digest)):
            raise ValueError('invalid operational size or checksum metadata')
        paths.append(value)
    if len(set(paths)) != len(paths):
        raise ValueError('duplicate operational file entry')
    if not REQUIRED_OPERATIONAL_FILES.issubset(paths):
        raise ValueError('incomplete operational file inventory')
    # Validate the complete inventory before hashing files or accessing model data.
    for entry in entries:
        verify_file(contained(ROOT, entry['path']), entry)


def model_path(value, prefix):
    if not isinstance(value, str) or '\x00' in value or '\\' in value:
        raise ValueError('invalid model metadata path')
    path = PurePosixPath(value)
    if (not value.startswith(prefix) or path.is_absolute() or '..' in path.parts
            or path.as_posix() != value):
        raise ValueError('unsafe model metadata path')
    return path


def embedded_metadata(model):
    """Small sealed model configuration belongs in Git; weights never do."""
    if 'embedded_small_blobs' not in model:
        return {}
    entries = model['embedded_small_blobs']
    if not isinstance(entries, list) or not entries:
        raise ValueError('invalid embedded model configuration inventory')
    expected = {entry['path']: entry for entry in model['blobs']
                if entry.get('media_type') in SMALL_BLOB_MEDIA_TYPES}
    result = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError('invalid embedded model configuration entry')
        path = entry.get('path')
        if not isinstance(path, str) or path not in expected or path in result:
            raise ValueError('unknown or duplicate embedded model configuration')
        original = expected[path]
        if (type(entry.get('size')) is not int
                or not 0 <= entry['size'] <= SMALL_BLOB_LIMIT
                or any(entry.get(key) != original.get(key)
                       for key in ('size', 'sha256', 'media_type'))
                or not isinstance(entry.get('utf8'), str)):
            raise ValueError('invalid embedded model configuration metadata')
        raw = entry['utf8'].encode('utf-8')
        if (len(raw) != entry['size']
                or hashlib.sha256(raw).hexdigest() != entry['sha256']):
            raise ValueError('embedded model configuration checksum mismatch')
        result[path] = raw
    if set(result) != set(expected):
        raise ValueError('incomplete embedded model configuration inventory')
    return result


def model_metadata(manifest):
    """Validate the embedded activation manifest before any target can be written."""
    if not isinstance(manifest, dict) or not isinstance(manifest.get('model'), dict):
        raise ValueError('invalid model metadata')
    model = manifest['model']
    model_path(model['manifest_path'], 'manifests/')
    raw = model['manifest_utf8'].encode('utf-8')
    if hashlib.sha256(raw).hexdigest() != model['manifest_sha256']:
        raise ValueError('embedded manifest checksum mismatch')
    # Reject inconsistent locks before writing anything.
    image = json.loads(raw)
    expected = {x['digest'].replace('sha256:', 'blobs/sha256-'): x['size']
                for x in [image['config']] + image['layers']}
    actual = {x['path']: x['size'] for x in model['blobs']}
    if expected != actual or len(actual) != len(model['blobs']):
        raise ValueError('inconsistent blob inventory')
    for entry in model['blobs']:
        model_path(entry['path'], 'blobs/')
        if (type(entry.get('size')) is not int or entry['size'] < 0
                or not isinstance(entry.get('sha256'), str)
                or len(entry['sha256']) != 64
                or any(char not in '0123456789abcdef' for char in entry['sha256'])):
            raise ValueError('invalid model blob size or checksum metadata')
        if entry['path'] != 'blobs/sha256-' + entry['sha256']:
            raise ValueError('inconsistent blob identity')
    embedded_metadata(model)
    links = model.get('manifest_links', [])
    if not isinstance(links, list) or any(not isinstance(link, dict) for link in links):
        raise ValueError('invalid model namespace link inventory')
    paths = []
    for link in links:
        path = model_path(link['path'], 'manifests-v2/')
        target_blob = 'blobs/sha256-' + link['target_sha256']
        if (link['target_sha256'] != model['runtime_digest']
                or actual.get(target_blob) != link['target_size']):
            raise ValueError('model namespace target is not the approved manifest blob')
        expected_target = posixpath.relpath(target_blob, path.parent.as_posix())
        if (link['target'] != expected_target or
                hashlib.sha256(link['target'].encode('utf-8')).hexdigest() != link['link_text_sha256']):
            raise ValueError('model namespace link target or checksum mismatch')
        paths.append(path.as_posix())
    if len(set(paths)) != len(paths) or any(
            a.startswith(b + '/') for a in paths for b in paths if a != b):
        raise ValueError('duplicate or overlapping model namespace paths')
    return model, raw


def check_store(manifest, store):
    model, raw = model_metadata(manifest)
    for entry in model['blobs']:
        verify_file(contained(store, entry['path']), entry)
    disk_manifest = contained(store, model['manifest_path'])
    if disk_manifest.read_bytes() != raw:
        raise ValueError('model manifest mismatch')
    for link in model.get('manifest_links', []):
        relative = PurePosixPath(link['path'])
        parent = contained(store, relative.parent.as_posix())
        path = parent / relative.name
        if not path.is_symlink() or os.readlink(path) != link['target']:
            raise ValueError('model namespace link missing or mismatched')


def publish_manifests(manifest, target):
    """Caller verifies all blobs first; only reviewed activation entries follow."""
    model, raw = model_metadata(manifest)
    for link in model.get('manifest_links', []):
        relative = PurePosixPath(link['path'])
        parent = contained(target, relative.parent.as_posix())
        parent.mkdir(parents=True, exist_ok=True)
        (parent / relative.name).symlink_to(link['target'])
    destination = contained(target, model['manifest_path'])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def restore(manifest, source, target):
    check_store(manifest, source)
    contained(target, 'blobs')
    # Caller must choose a missing directory. Existing weights are never replaced.
    target.mkdir(parents=False, exist_ok=False)
    model = manifest['model']
    for entry in model['blobs']:
        destination = contained(target, entry['path'])
        destination.parent.mkdir(parents=True, exist_ok=True)
        with contained(source, entry['path']).open('rb') as src, destination.open('xb') as dst:
            shutil.copyfileobj(src, dst, 8 * 1024 * 1024)
            dst.flush()
            os.fsync(dst.fileno())
        verify_file(destination, entry)
    # No installed model is visible before every copied blob passes verification.
    publish_manifests(manifest, target)
    check_store(manifest, target)


def runtime_check(manifest):
    # Read-only request from the existing backend; never pull or generate a model.
    code = ('puts JSON.generate(tags: JSON.parse(Net::HTTP.get(URI("http://ollama:11434/api/tags"))), '
            'version: JSON.parse(Net::HTTP.get(URI("http://ollama:11434/api/version"))))')
    result = subprocess.run(['docker', 'compose', 'exec', '-T', 'backend',
                             'ruby', '-rnet/http', '-rjson', '-e', code], cwd=ROOT,
                            check=True, capture_output=True, text=True, timeout=30)
    runtime = json.loads(result.stdout)
    if runtime['version']['version'] != manifest['runtime']['ollama_version']:
        raise ValueError('Ollama runtime version mismatch; review the pinned environment')
    models = runtime['tags']['models']
    model = manifest['model']
    matches = [m for m in models if m['name'] == model['name']]
    if len(matches) != 1 or matches[0]['digest'] != model['runtime_digest']:
        raise ValueError('runtime model identity mismatch; no fallback allowed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['knowledge', 'verify', 'restore', 'runtime'])
    parser.add_argument('--store', type=Path, default=ROOT / 'ollama/models')
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    manifest = load_manifest()
    check_knowledge(manifest)
    model_metadata(manifest)
    if args.action == 'restore':
        if args.source is None:
            parser.error('restore requires --source APPROVED_OFFLINE_MODELS_DIRECTORY')
        restore(manifest, args.source.absolute(), args.store.absolute())
    elif args.action in ('verify', 'runtime'):
        check_store(manifest, args.store.absolute())
    if args.action == 'runtime':
        runtime_check(manifest)
    print(json.dumps({'status': 'verified', 'action': args.action,
                      'model': manifest['model']['name'],
                      'runtime_digest': manifest['model']['runtime_digest'],
                      'git_embedded_small_blobs': len(embedded_metadata(manifest['model'])),
                      'knowledge_files': len(manifest['operational_files'])}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('recovery refused: ' + str(error), file=sys.stderr)
        sys.exit(1)
