#!/usr/bin/env python3
"""Optional verified launcher for the bundled, stateless Go syntax inspector."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys

TOOL_ROOT = Path(__file__).resolve().parent / 'go-source-ast'
MAX_REQUEST = 3 * 1024 * 1024


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def executable(tool_root=TOOL_ROOT, system=None, machine=None):
    """Verify all executable inputs before choosing a native packaged binary."""
    manifest_path = tool_root / 'manifest.json'
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError('missing or unsafe Go tool manifest')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 1 or manifest.get('profile') != 'go-standard-parser-declarations-v1':
        raise ValueError('unsupported Go tool manifest')
    for name, key in [('main.go', 'source_sha256'), ('GO-LICENSE', 'license_sha256')]:
        path = tool_root / name
        if path.is_symlink() or not path.is_file() or checksum(path) != manifest[key]:
            raise ValueError('Go producer source/license integrity mismatch')
    system = (system or platform.system()).lower()
    machine = (machine or platform.machine()).lower()
    machine = {'aarch64': 'arm64', 'x86_64': 'amd64'}.get(machine, machine)
    name = 'go-source-ast-' + system + '-' + machine
    record = manifest.get('binaries', {}).get(name)
    if not record or record.get('path') != 'bin/' + name:
        raise ValueError('Go AST tool unavailable for this platform')
    binary = tool_root / 'bin' / name
    if binary.is_symlink() or binary.parent.is_symlink() or not binary.is_file():
        raise ValueError('unsafe or missing Go producer binary')
    if binary.stat().st_size != record['bytes'] or checksum(binary) != record['sha256']:
        raise ValueError('Go producer binary integrity mismatch')
    return binary, manifest, checksum(manifest_path)


def run(raw, tool_root=TOOL_ROOT):
    if len(raw) > MAX_REQUEST:
        raise ValueError('Go AST request too large')
    binary, manifest, manifest_sha = executable(tool_root)
    result = subprocess.run([str(binary)], input=raw, capture_output=True, timeout=15)
    if result.returncode < 0:
        raise ValueError('Go parser process terminated by signal ' + str(-result.returncode))
    if result.returncode:
        raise ValueError(result.stderr.decode('utf-8', errors='replace').strip()[:1500] or 'Go parser refused source')
    if len(result.stdout) > 128 * 1024:
        raise ValueError('oversized Go parser response')
    packet = json.loads(result.stdout)
    if packet.get('profile') != manifest['profile'] or packet.get('source_executed') is not False or packet.get('syntax_only') is not True:
        raise ValueError('unexpected Go parser response profile')
    packet['producer'] = {'source_sha256': manifest['source_sha256'],
                          'binary_sha256': checksum(binary),
                          'manifest_sha256': manifest_sha,
                          'launcher_sha256': checksum(Path(__file__).resolve()),
                          'version': manifest['version']}
    return packet


if __name__ == '__main__':
    try:
        raw = sys.stdin.buffer.read(MAX_REQUEST + 1)
        json.dump(run(raw), sys.stdout, ensure_ascii=False)
        sys.stdout.write('\n')
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        print('Go AST tool refused: ' + str(error), file=sys.stderr)
        sys.exit(2)
