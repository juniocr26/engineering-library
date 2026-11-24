"""Owned timeout fault at cached revalidation versus fresh extraction; no real hang."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / 'agent/tools'))
import documentation_retrieval as retrieval

out = Path('/private/tmp/el-helper-cached-timeout-boundary-v1')
source = out / 'source'
journal = out / 'journal'
source.mkdir(parents=True, exist_ok=False)
journal.mkdir()
raw = b'package owned\n\nfunc Selected() int { return 7 }\n'
(source / 'owned.go').write_bytes(raw)
registry = {'owned': {'root': str(source), 'revision': 'c' * 40, 'files': {'owned.go': {'sha256': retrieval.sha(raw), 'language': 'go', 'selectors': ['Selected']}}}}
request = {'request_id': 'cached', 'source_id': 'owned', 'revision': 'c' * 40, 'path': 'owned.go', 'qualified_symbol': 'Selected', 'expected_sha256': retrieval.sha(raw)}
helper = retrieval.HelperRetrieval(registry, str(journal))
initial = helper.request(request)
assert initial['status'] == 'FOUND', initial
before = {f.name: retrieval.sha(f.read_bytes()) for f in journal.iterdir()}
original = retrieval.extract
calls = []
def injected_timeout(*args):
    calls.append({'language': args[2], 'selector': args[1]})
    raise subprocess.TimeoutExpired(cmd='owned-fault-no-process-started', timeout=20)
retrieval.extract = injected_timeout
try:
    try:
        returned = helper.request(request)
        cached = {'returned': returned, 'raised': None}
    except subprocess.TimeoutExpired as error:
        cached = {'raised': type(error).__name__, 'message': str(error), 'returned': None}
    after_cached = {f.name: retrieval.sha(f.read_bytes()) for f in journal.iterdir()}
    fresh = helper.request({**request, 'request_id': 'fresh'})
finally:
    retrieval.extract = original
assert cached['raised'] == 'TimeoutExpired'
assert before == after_cached
assert fresh['status'] == 'INCONCLUSIVE'
assert helper._request_lock.acquire(blocking=False)
helper._request_lock.release()
files = []
for file in sorted(out.rglob('*')):
    if file.is_file(): files.append({'path': str(file.relative_to(out)), 'bytes': file.stat().st_size, 'sha256': retrieval.sha(file.read_bytes())})
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'KNOWN_BOUNDED_ERROR_DELIVERY_GAP_NO_SOURCE_CHANGE', 'tool_version': retrieval.VERSION, 'tool_sha256': retrieval.sha(Path(retrieval.__file__).read_bytes()), 'hypothesis': 'Cached Go revalidation newly calls a subprocess-producing extractor outside the inner fresh-extraction SubprocessError handler; an injected TimeoutExpired escapes instead of returning refusal.', 'initial_native_selected_source_parse': initial, 'fault': 'In-process replacement of extract raising TimeoutExpired; no real timeout, hung child, compiler outage or source execution observed.', 'cached_observation': cached, 'fresh_observation': fresh, 'cached_journal_bytes_unchanged': before == after_cached, 'request_lock_released': True, 'fault_calls': calls, 'owned_root': str(out), 'files': files, 'source_executed': False, 'production_source_changed': False, 'model_calls': 0, 'optimizer_steps': 0, 'next_bounded_fix': 'Review explicit delivery semantics for subprocess failures during cached Go validation; preserve journals and request locks. Do not silently retry or assume fresh/cached failures are identical. Current 0.1.5 lexical-integrity success is not uniform operational-error handling.', 'training_excluded': True, 'independent_holdout': False}
with (P / 'helper-cached-timeout-boundary-v1.json').open('x') as stream:
    json.dump(record, stream, indent=2); stream.write('\n')
print(json.dumps({'cached_raised': cached['raised'], 'fresh_status': fresh['status'], 'journal_unchanged_for_cached': before == after_cached, 'request_lock_released': True, 'owned_files': len(files)}))
