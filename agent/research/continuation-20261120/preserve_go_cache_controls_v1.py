"""Preserve exact owned cache controls and verify legacy journal nonmigration."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import tarfile

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / 'agent/tools'))
import documentation_retrieval as helper

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def identities(root):
    rows = []
    for path in sorted(root.rglob('*')):
        if path.is_file():
            assert not path.is_symlink()
            stat = path.stat()
            rows.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': stat.st_size,
                         'mtime_ns': stat.st_mtime_ns, 'mode': stat.st_mode & 0o777})
    return rows

legacy_rows = []
base = P / 'helper-go-cached-controls-baseline-v1'
for case in ['valid-function', 'valid-method', 'substituted-other-function']:
    owned = base / case
    before = identities(owned)
    inputs = json.loads((owned / 'inputs.json').read_text())
    observed = helper.HelperRetrieval(inputs['registry'], str((owned / 'journal').resolve())).request(inputs['request'])
    after = identities(owned)
    assert observed['status'] == 'LEGACY_RESULT_REVIEW_REQUIRED', observed
    assert before == after
    legacy_rows.append({'id': case, 'observed': observed, 'all_file_bytes_modes_mtimes_unchanged': True,
                        'before_and_after': before})

destination = ROOT / '.local-backups/continuation-20261120/helper-go-cache-controls-v1'
destination.mkdir(exist_ok=False)
archive = destination / 'owned-controls.tar.gz'
files = []
for directory in [base, P / 'helper-go-cached-controls-candidate-v2']:
    files += [ROOT / row['path'] for row in identities(directory)]
records = [{'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size} for path in files]
with tarfile.open(archive, 'w:gz') as tar:
    for path in files:
        tar.add(path, arcname=str(path.relative_to(ROOT)), recursive=False)
with tarfile.open(archive) as tar:
    members = tar.getmembers()
    assert len(members) == len(records) and all(member.isfile() for member in members)
    expected = {row['path']: row for row in records}
    for member in members:
        raw = tar.extractfile(member).read()
        assert len(raw) == expected[member.name]['bytes'] and hashlib.sha256(raw).hexdigest() == expected[member.name]['sha256']
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'helper_version': helper.VERSION,
          'helper_sha256': sha(Path(helper.__file__)), 'archive': str(archive.relative_to(ROOT)),
          'archive_sha256': sha(archive), 'archive_bytes': archive.stat().st_size, 'members': records,
          'legacy_readbacks': legacy_rows, 'all_members_stream_verified': True,
          'no_automatic_legacy_migration': True, 'originals_retained': True, 'source_executed': False,
          'model_calls': 0, 'optimizer_steps': 0, 'remote_durability': False}
with (P / 'helper-go-cache-preservation-v1.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'members': len(records), 'bytes': archive.stat().st_size,
                  'legacy_readbacks_unchanged': len(legacy_rows), 'archive_sha256': record['archive_sha256']}))
