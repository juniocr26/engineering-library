"""Acquire/reuse only frozen Git-blob-verified public cachetools source and notices."""
from concurrent.futures import ThreadPoolExecutor
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
metadata_path = P / 'cachetools-selected-source-metadata-v1.json'
metadata = json.loads(metadata_path.read_text())
target = P / 'new-public-sources-v1/tkem--cachetools'
previous = ROOT / '.local-backups/documentation-intelligence-20261119/cachetools-real-evolution-v1/previous'
tasks = [(cut, item) for cut in metadata['rows'] for item in cut['selected_blob_metadata']]

def acquire(task):
    cut, item = task
    name = item['path']
    old = previous / name
    reused = cut['tag'] == 'v5.3.3' and old.is_file()
    url = 'https://raw.githubusercontent.com/tkem/cachetools/' + cut['revision'] + '/' + name
    if reused:
        raw = old.read_bytes()
    else:
        request = urllib.request.Request(url, headers={'User-Agent': 'EngineeringLibrarySourceResearch/1.0'})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(65537)
        assert len(raw) <= 65536
    assert len(raw) == item['size']
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == item['sha']
    path = target / cut['revision'] / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)
    return {'tag': cut['tag'], 'revision': cut['revision'], 'upstream_path': name,
            'path': str(path.relative_to(ROOT)), 'url': url, 'git_blob': item['sha'],
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
            'reused_exact_old_snapshot': reused, 'previous_path': str(old.relative_to(ROOT)) if reused else None}

with ThreadPoolExecutor(max_workers=4) as executor:
    rows = list(executor.map(acquire, tasks))
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'repository': 'tkem/cachetools',
          'metadata_sha256': hashlib.sha256(metadata_path.read_bytes()).hexdigest(), 'files': rows,
          'all_git_blobs_verified': True, 'source_executed': False, 'package_installed': False,
          'external_repository_modified': False, 'owner_approved': False, 'training_gold': False,
          'prior_family_exposure': 'cachetools-prior-exposure-reconciliation-v1.json'}
with (P / 'cachetools-source-provenance-v1.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'files': len(rows), 'bytes': sum(row['bytes'] for row in rows),
                  'reused_old_files': sum(row['reused_exact_old_snapshot'] for row in rows)}))
