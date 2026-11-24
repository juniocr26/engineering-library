"""Consume current helper and manual review bundle from the verified V6 restore."""
import datetime
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tarfile

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parents[2]
receipt = json.loads((P / 'recovery-delta-receipt-v6.json').read_text())
RESTORE = Path(receipt['restored_root'])
manifest_path = ROOT / receipt['input_manifest']['path']

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

assert sha(manifest_path) == receipt['input_manifest']['sha256']
manifest = json.loads(manifest_path.read_text())
expected = manifest['effective_expected_files']
for name, identity in expected.items():
    assert sha(RESTORE / name) == identity['sha256'], name
sys.path.insert(0, str(RESTORE / 'agent/tools'))
spec = importlib.util.spec_from_file_location('current_restored_helper_v6', RESTORE / 'agent/tools/documentation_retrieval.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
import documentation_workspace as workspace
assert Path(helper.__file__).resolve().is_relative_to(RESTORE)
assert Path(workspace.__file__).resolve().is_relative_to(RESTORE)
assert helper.VERSION == '0.1.5'
operational = json.loads((RESTORE / 'agent/recovery/manifest.json').read_text())
pin = next(row for row in operational['operational_files'] if row['path'] == 'agent/tools/documentation_retrieval.py')
assert sha(Path(helper.__file__)) == pin['sha256']

state = Path('/private/tmp/el-engineering-library-continuation-20261120-cut-v6-consumption')
state.mkdir(exist_ok=False)
source, journal = state / 'source', state / 'go-journal'
source.mkdir()
journal.mkdir()
research = RESTORE / 'agent/research/continuation-20261120'
oracle = json.loads((research / 'helper-go-cached-unit-oracle-v2.json').read_text())
raw = oracle['source'].encode()
assert hashlib.sha256(raw).hexdigest() == oracle['source_sha256']
(source / 'owned.go').write_bytes(raw)
registry = {'owned-go': {'root': str(source), 'revision': 'b' * 40,
    'files': {'owned.go': {'sha256': oracle['source_sha256'], 'language': 'go', 'selectors': ['owned.Selected', 'Other']}}}}
request = {'request_id': 'restore-go-selected', 'source_id': 'owned-go', 'revision': 'b' * 40,
           'path': 'owned.go', 'qualified_symbol': 'owned.Selected', 'expected_sha256': oracle['source_sha256']}
tool = helper.HelperRetrieval(registry, str(journal))
fresh = tool.request(request)
assert fresh['status'] == 'FOUND', fresh
duplicate = helper.HelperRetrieval(registry, str(journal)).request(request)
assert duplicate['status'] == 'DUPLICATE', duplicate
result_path = journal / 'restore-go-selected.result.json'
receipt_path = journal / 'restore-go-selected.receipt.json'
(state / 'go-result-before-controlled-rewrite.json').write_bytes(result_path.read_bytes())
(state / 'go-receipt-before-controlled-rewrite.json').write_bytes(receipt_path.read_bytes())
cached = json.loads(result_path.read_text())
cached['evidence'].update(helper.extract(raw.decode(), 'Other', 'go'))
cached['evidence']['selector'] = 'owned.Selected'
cached['quote_bytes'] = len(cached['evidence']['quote'].encode())
cached['cumulative_quote_bytes'] = cached['quote_bytes']
encoded = helper.canonical(cached)
result_path.write_bytes(encoded)
coordinated = helper.receipt_for(encoded, helper.canonical(request), tool.registry_sha256, oracle['source_sha256'], cached['extractor_identity'])
receipt_path.write_bytes(helper.canonical(coordinated))
refused = helper.HelperRetrieval(registry, str(journal)).request(request)
assert refused['status'] == 'REFUSED', refused
assert sha(source / 'owned.go') == oracle['source_sha256']

provenance = json.loads((research / 'cachetools-source-provenance-v1.json').read_text())
entry = next(row for row in provenance['files'] if row['tag'] == 'v6.0.0' and row['upstream_path'] == 'src/cachetools/__init__.py')
physical = RESTORE / entry['path']
python_journal = state / 'python-journal'
python_journal.mkdir()
python_registry = {'cache-source': {'root': str(physical.parent), 'revision': entry['revision'],
    'files': {'__init__.py': {'sha256': entry['sha256'], 'language': 'python', 'selectors': ['TTLCache.expire']}}}}
python_request = {'request_id': 'restore-python-expire', 'source_id': 'cache-source', 'revision': entry['revision'],
    'path': '__init__.py', 'qualified_symbol': 'TTLCache.expire', 'expected_sha256': entry['sha256']}
python_result = helper.HelperRetrieval(python_registry, str(python_journal)).request(python_request)
assert python_result['status'] == 'FOUND', python_result
assert python_result['evidence'] == helper.python_unit(physical.read_text(), 'TTLCache.expire')

bundle = research / 'cachetools-lifecycle-candidates-v1'
bundle_manifest = json.loads((bundle / 'manifest.json').read_text())
assert bundle_manifest['production_candidate_applier_used'] is False
assert bundle_manifest['physical_published_documentation_certified'] is False
for binding in bundle_manifest['source_bindings']:
    assert sha(RESTORE / binding['path']) == binding['sha256']
diffs = {'en': [], 'pt-br': []}
present, absent = 0, 0
with workspace.directory(str(bundle)) as fd:
    for item in bundle_manifest['entries']:
        contents = {}
        for side, field in [('previous', 'previous_path'), ('candidate', 'candidate_path')]:
            identity = item[side]
            try:
                value, metadata = workspace.read(fd, item[field], 16384)
            except FileNotFoundError:
                assert identity['exists'] is False
                value = b''
                absent += 1
            else:
                assert identity['exists'] is True and metadata['sha256'] == identity['sha256']
                present += 1
            contents[side] = value
        if item['manual_reference_action'] in ['NO-OP', 'INCONCLUSIVE']:
            assert contents['previous'] == contents['candidate']
        diffs[item['language']].extend(difflib.unified_diff(contents['previous'].decode().splitlines(keepends=True),
            contents['candidate'].decode().splitlines(keepends=True), fromfile=item['previous_path'], tofile=item['candidate_path']))
for language in ['en', 'pt-br']:
    assert (bundle / (language + '.patch.diff')).read_text() == ''.join(diffs[language])
assert (present, absent) == (24, 4)
for name, identity in expected.items():
    assert sha(RESTORE / name) == identity['sha256'], 'restored input changed: ' + name

inputs = {'go_registry': registry, 'go_request': request, 'python_registry': python_registry, 'python_request': python_request,
          'operator_root_rebinding': 'New explicit registries only; original journals and cached budget state are not migrated.'}
(state / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n')
backup = ROOT / '.local-backups/continuation-20261120/restored-consumption-v6'
backup.mkdir(exist_ok=False)
archive = backup / 'owned-fresh-journals-and-controlled-cache.tar.gz'
members = [{'path': str(path.relative_to(state)), 'sha256': sha(path), 'bytes': path.stat().st_size}
           for path in sorted(state.rglob('*')) if path.is_file()]
with tarfile.open(archive, 'w:gz') as tar:
    for member in members:
        tar.add(state / member['path'], arcname=member['path'], recursive=False)
with tarfile.open(archive) as tar:
    assert len(tar.getmembers()) == len(members)
    expected_members = {row['path']: row for row in members}
    for member in tar.getmembers():
        assert member.isfile()
        raw_member = tar.extractfile(member).read()
        assert hashlib.sha256(raw_member).hexdigest() == expected_members[member.name]['sha256']
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'CURRENT_RESTORED_HELPER_AND_REVIEW_BUNDLE_CONSUMED',
    'restored_root': str(RESTORE), 'effective_expected_files_verified_before_and_after': len(expected),
    'restored_helper_version': helper.VERSION, 'restored_helper_sha256': sha(Path(helper.__file__)),
    'helper_loaded_from_restore': True, 'workspace_loaded_from_restore': True,
    'go_fresh': fresh, 'go_duplicate': duplicate, 'go_coordinated_substitution': refused, 'python_fresh': python_result,
    'review_bundle_present_documents': present, 'review_bundle_verified_absences': absent,
    'review_bundle_diff_languages_reconstructed': 2, 'review_bundle_source_files_pinned': len(bundle_manifest['source_bindings']),
    'archive': {'path': str(archive.relative_to(ROOT)), 'sha256': sha(archive), 'bytes': archive.stat().st_size, 'members': members},
    'original_restore_files_unchanged': True, 'source_executed': False, 'model_calls': 0,
    'native_public_library_experiments_rerun': False, 'new_independent_cases': 0,
    'original_journals_automatically_migrated': False, 'model_weights_copied': False,
    'owner_approved': False, 'training_gold': False, 'publication': False,
    'limits': 'Selected current source/evidence/consumer recovery in an existing host. New operator registries and owned journals only; no full OS/cold boot, remote durability, actual published catalog certification or training checkpoint recovery.'}
with (P / 'restored-research-consumption-v6.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({'files_unchanged': len(expected), 'helper': helper.VERSION,
                 'go_statuses': [fresh['status'], duplicate['status'], refused['status']],
                 'python_status': python_result['status'], 'review_documents': present, 'verified_absences': absent,
                 'archive_members': len(members)}))
