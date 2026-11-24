"""Freeze pinned transport/exception source scope before reading any bodies."""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
REPOSITORY = 'encode/httpx'


def get(url, limit=1048576):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}), timeout=35) as response:
        raw = response.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('bounded public metadata response exceeded')
    return raw


rows = []
for tag in ['0.25.2', '0.28.1']:
    url = 'https://api.github.com/repos/' + REPOSITORY + '/git/ref/tags/' + tag
    raw = get(url, 65536)
    with (P / ('httpx-' + tag + '-ref-v1.json')).open('xb') as stream:
        stream.write(raw)
    ref = json.loads(raw)
    obj = ref['object']
    if obj['type'] == 'tag':
        tag_raw = get(obj['url'], 65536)
        with (P / ('httpx-' + tag + '-tag-v1.json')).open('xb') as stream:
            stream.write(tag_raw)
        obj = json.loads(tag_raw)['object']
    assert obj['type'] == 'commit'
    revision = obj['sha']
    tree_url = 'https://api.github.com/repos/' + REPOSITORY + '/git/trees/' + revision + '?recursive=1'
    tree_raw = get(tree_url)
    tree = json.loads(tree_raw)
    assert tree['truncated'] is False
    with (P / ('httpx-' + tag + '-tree-v1.json')).open('xb') as stream:
        stream.write(tree_raw)
    wanted = {'httpx/_transports/default.py', 'httpx/_exceptions.py', 'pyproject.toml', 'LICENSE.md', 'LICENSE'}
    entries = [entry for entry in tree['tree'] if entry['type'] == 'blob' and entry['path'] in wanted]
    assert {'httpx/_transports/default.py', 'httpx/_exceptions.py', 'pyproject.toml'}.issubset({entry['path'] for entry in entries})
    assert any(entry['path'] in {'LICENSE', 'LICENSE.md'} for entry in entries)
    rows.append({'tag': tag, 'revision': revision, 'ref_url': url, 'tree_url': tree_url, 'tree_sha256': hashlib.sha256(tree_raw).hexdigest(), 'selected_blobs': entries, 'source_bodies_fetched': False})
producers = {}
for name in ['architecture_fact_observer_v3.py', 'architecture_claim_compiler_v4.py', 'module_contract_observer_v5.py', 'class_member_observer_v3.py', 'keyword_prefix_observer_v1.py', 'registered_claim_batch_v1.py']:
    producers[name] = hashlib.sha256((P / name).read_bytes()).hexdigest()
# Measured bounded text exposure only. Related framework dependency names are exposure, not pristine holdout evidence.
baseline = json.loads((P / 'baseline.json').read_text())
hits = []
scanned = 0
bytes_scanned = 0
for name in baseline['tracked_identity']:
    path = ROOT / name
    if not path.is_file() or path.suffix.lower() not in {'.md', '.py', '.json', '.jsonl', '.toml', '.txt', '.lock', '.rb', '.js', '.ts'} or path.stat().st_size > 4 * 1024 * 1024:
        continue
    raw = path.read_bytes()
    scanned += 1
    bytes_scanned += len(raw)
    folded = raw.lower()
    needles = [needle for needle in [b'encode/httpx', b'httpx', b'map_httpcore_exceptions'] if needle in folded]
    if needles:
        hits.append({'path': name, 'needles': [needle.decode() for needle in needles], 'sha256': hashlib.sha256(raw).hexdigest()})
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'repository': REPOSITORY, 'source_body_inspection_started': False, 'revisions': rows, 'frozen_producers': producers,
          'evaluation_task': 'Cross-file written transport exception mapping, context-manager boundaries, declared target exception hierarchy, dependency constraints and source citations; no HTTP requests or transport runtime guarantees.',
          'existing_profile_limits': 'Owned architecture compiler admits an exact five-file registry, not arbitrary HTTPX modules. Module observer refuses decorated contracts. New source-reviewed facts do not by themselves constitute a general resolver improvement.',
          'exposure_preflight': {'tracked_text_files': scanned, 'bytes': bytes_scanned, 'hits': hits, 'ignored_archives_or_external_environments_scanned': False, 'related_framework_dependency_ancestry_possible': True},
          'certified_neural_holdout': False, 'newly_inspected_implementation_family_only': True, 'source_execution_allowed': False, 'model_calls_planned': 0, 'training_excluded': True, 'owner_approved': False, 'training_gold': False, 'permanent_tests_or_production_changes_authorized': False}
with (P / 'httpx-source-family-freeze-v1.json').open('x') as stream:
    stream.write(json.dumps(record, indent=2) + '\n')
print(json.dumps({'revisions': [(row['tag'], row['revision']) for row in rows], 'selected_blob_counts': [len(row['selected_blobs']) for row in rows], 'source_bodies_fetched': False, 'tracked_text_files_scanned': scanned, 'prior_exposure_hit_files': len(hits), 'certified_holdout': False}))
