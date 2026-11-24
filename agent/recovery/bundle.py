#!/usr/bin/env python3
"""Prepare and restore local, checksummed parts suitable for later LFS review."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys

from bootstrap import ROOT, check_knowledge, check_store, contained, embedded_metadata, model_metadata, publish_manifests, verify_file, load_manifest

CHUNK_BYTES = 256 * 1024 * 1024
BUFFER_BYTES = 1024 * 1024


def pack(lock, source, target, chunk_bytes=CHUNK_BYTES):
    if type(chunk_bytes) is not int or not 1 <= chunk_bytes <= CHUNK_BYTES:
        raise ValueError('invalid bundle part size')
    check_store(lock, source)
    contained(target, 'parts')
    target.mkdir(exist_ok=False)
    (target / 'parts').mkdir()
    index = {'schema_version': 1, 'model_digest': lock['model']['runtime_digest'],
             'chunk_bytes': chunk_bytes, 'artifacts': []}
    for entry in lock['model']['blobs']:
        artifact = {key: entry[key] for key in ('path', 'size', 'sha256')}
        artifact['parts'] = []
        with contained(source, entry['path']).open('rb') as src:
            remaining = entry['size']
            number = 0
            while remaining:
                relative = 'parts/' + entry['sha256'] + f'.part-{number:06d}'
                amount = min(chunk_bytes, remaining)
                digest = hashlib.sha256()
                with contained(target, relative).open('xb') as dst:
                    left = amount
                    while left:
                        block = src.read(min(BUFFER_BYTES, left))
                        if not block:
                            raise ValueError('source ended while packing')
                        dst.write(block)
                        digest.update(block)
                        left -= len(block)
                    dst.flush()
                    os.fsync(dst.fileno())
                artifact['parts'].append({'path': relative, 'size': amount,
                                          'sha256': digest.hexdigest()})
                remaining -= amount
                number += 1
        index['artifacts'].append(artifact)
    # The lock supplies the original manifest and licenses are included as blobs.
    verify_bundle(lock, index, target)
    with (target / 'bundle.json').open('x') as stream:
        json.dump(index, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return index


def bundle_layout(lock, index):
    """Validate every index entry before any model payload is read."""
    model_metadata(lock)
    if (not isinstance(index, dict)
            or type(index.get('schema_version')) is not int
            or index['schema_version'] != 1
            or index.get('model_digest') != lock['model']['runtime_digest']):
        raise ValueError('bundle model identity mismatch')
    chunk_bytes = index.get('chunk_bytes')
    if type(chunk_bytes) is not int or not 1 <= chunk_bytes <= CHUNK_BYTES:
        raise ValueError('invalid bundle part size')
    expected = {entry['path']: entry for entry in lock['model']['blobs']}
    entries = index.get('artifacts')
    if (not isinstance(entries, list)
            or any(not isinstance(entry, dict) for entry in entries)):
        raise ValueError('invalid bundle artifact inventory')
    if len(entries) != len(expected) or {e['path'] for e in entries} != set(expected):
        raise ValueError('bundle artifact inventory mismatch')
    for artifact in entries:
        entry = expected[artifact['path']]
        if (type(artifact.get('size')) is not int
                or any(artifact.get(key) != entry[key] for key in ('size', 'sha256'))
                or not isinstance(artifact.get('parts'), list)):
            raise ValueError('bundle artifact identity mismatch')
        remaining = entry['size']
        for number, part in enumerate(artifact['parts']):
            relative = 'parts/' + entry['sha256'] + f'.part-{number:06d}'
            if (not isinstance(part, dict) or type(part.get('size')) is not int
                    or remaining <= 0 or part.get('path') != relative
                    or part['size'] != min(chunk_bytes, remaining)
                    or not isinstance(part.get('sha256'), str)
                    or len(part['sha256']) != 64
                    or any(char not in '0123456789abcdef' for char in part['sha256'])):
                raise ValueError('bundle part layout mismatch')
            remaining -= part['size']
        if remaining:
            raise ValueError('incomplete bundle part inventory')
    return entries


def open_part(source, artifact, part, number, chunk_bytes, embedded):
    path = contained(source, part['path'])
    if path.exists() or artifact['path'] not in embedded:
        # A present corrupt part is always refused, never replaced by Git bytes.
        verify_file(path, part)
        return path.open('rb')
    raw = embedded[artifact['path']]
    offset = number * chunk_bytes
    data = raw[offset:offset + part['size']]
    if len(data) != part['size'] or hashlib.sha256(data).hexdigest() != part['sha256']:
        raise ValueError('embedded configuration part checksum mismatch')
    return io.BytesIO(data)


def verify_bundle(lock, index, source):
    entries = bundle_layout(lock, index)
    embedded = embedded_metadata(lock['model'])
    for artifact in entries:
        digest = hashlib.sha256()
        for number, part in enumerate(artifact['parts']):
            with open_part(source, artifact, part, number, index['chunk_bytes'], embedded) as stream:
                for block in iter(lambda: stream.read(BUFFER_BYTES), b''):
                    digest.update(block)
        if digest.hexdigest() != artifact['sha256']:
            raise ValueError('reassembled artifact checksum mismatch')


def restore_bundle(lock, index, source, target):
    verify_bundle(lock, index, source)
    embedded = embedded_metadata(lock['model'])
    contained(target, 'blobs')
    target.mkdir(exist_ok=False)
    for artifact in index['artifacts']:
        destination = contained(target, artifact['path'])
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as dst:
            for number, part in enumerate(artifact['parts']):
                with open_part(source, artifact, part, number, index['chunk_bytes'], embedded) as src:
                    shutil.copyfileobj(src, dst, BUFFER_BYTES)
            dst.flush()
            os.fsync(dst.fileno())
        verify_file(destination, artifact)
    # Only activate a complete set of verified blobs.
    publish_manifests(lock, target)
    check_store(lock, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['pack', 'verify', 'restore'])
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--store', type=Path, default=ROOT / 'ollama/models')
    args = parser.parse_args()
    lock = load_manifest()
    check_knowledge(lock)
    if args.action == 'pack':
        index = pack(lock, args.store.absolute(), args.bundle.absolute())
    else:
        # Trust the reviewed Git index, not an index supplied with downloaded parts.
        index = json.loads((Path(__file__).parent / 'model-bundle.json').read_text())
        if args.action == 'restore':
            restore_bundle(lock, index, args.bundle.absolute(), args.store.absolute())
        else:
            verify_bundle(lock, index, args.bundle.absolute())
    print(json.dumps({'status': 'verified', 'action': args.action,
                      'model_digest': index['model_digest'],
                      'git_embedded_small_blobs': len(embedded_metadata(lock['model'])),
                      'parts': sum(len(e['parts']) for e in index['artifacts'])}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('bundle refused: ' + str(error), file=sys.stderr)
        sys.exit(1)
