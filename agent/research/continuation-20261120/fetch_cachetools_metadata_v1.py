"""Freeze public cachetools tag commits and complete tree metadata before code blobs."""
import datetime
import json
from pathlib import Path
import urllib.request

P = Path(__file__).resolve().parent
def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'EngineeringLibrarySourceResearch/1.0', 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(2 * 1024 * 1024 + 1)
        assert len(raw) <= 2 * 1024 * 1024
        return raw
def save(name, raw):
    with (P / name).open('xb') as stream:
        stream.write(raw)
rows = []
for tag in ['v5.3.3', 'v6.0.0']:
    raw = get('https://api.github.com/repos/tkem/cachetools/git/ref/tags/' + tag)
    save('cachetools-' + tag + '-ref-v1.json', raw)
    ref = json.loads(raw)
    target = ref['object']
    if target['type'] == 'tag':
        raw = get(target['url'])
        save('cachetools-' + tag + '-tag-object-v1.json', raw)
        target = json.loads(raw)['object']
    assert target['type'] == 'commit'
    revision = target['sha']
    raw = get('https://api.github.com/repos/tkem/cachetools/git/trees/' + revision + '?recursive=1')
    save('cachetools-' + tag + '-tree-v1.json', raw)
    tree = json.loads(raw)
    assert tree['sha'] == revision and tree['truncated'] is False
    files = [row for row in tree['tree'] if row['type'] == 'blob' and
             ((row['path'].startswith('src/cachetools/') and row['path'].endswith('.py')) or row['path'] in ['LICENSE', 'setup.py', 'setup.cfg', 'pyproject.toml'])]
    assert 1 <= len(files) <= 16
    rows.append({'tag': tag, 'revision': revision, 'selected_blob_metadata': files})
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'repository': 'tkem/cachetools',
          'rows': rows, 'source_bodies_acquired': False, 'source_executed': False,
          'owner_approved': False, 'training_gold': False}
with (P / 'cachetools-selected-source-metadata-v1.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'cuts': [{key: row[key] for key in ['tag', 'revision']} for row in rows],
                  'selected_blobs': [len(row['selected_blob_metadata']) for row in rows]}))
