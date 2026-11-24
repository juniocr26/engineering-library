"""Isolated method candidate for the newly observed cached subprocess-error gap."""
import datetime
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import textwrap

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
sys.path.insert(0, str(ROOT / 'agent/tools'))
import documentation_retrieval as retrieval

out = Path('/private/tmp/el-helper-timeout-delivery-candidate-v1')
out.mkdir(exist_ok=False)
original_source = textwrap.dedent(inspect.getsource(retrieval.HelperRetrieval._request))
old = 'except (RetrievalRefused, WorkspaceRefused, ValueError, OSError, UnicodeError, KeyError, TypeError, RecursionError) as error:'
new = 'except (RetrievalRefused, WorkspaceRefused, ValueError, OSError, UnicodeError, KeyError, TypeError, RecursionError, subprocess.SubprocessError) as error:'
assert original_source.count(old) == 1
candidate_source = original_source.replace(old, new)
(out / 'original-method.py').write_text(original_source)
(out / 'candidate-method.py').write_text(candidate_source)
namespace = dict(retrieval.__dict__)
exec(compile(candidate_source, '<owned-timeout-delivery-method-candidate>', 'exec'), namespace)
candidate_class = type('OwnedDeliveryCandidate', (retrieval.HelperRetrieval,), {'_request': namespace['_request']})
raw = b'package owned\n\nfunc Selected() int { return 7 }\n'
rows = []
original_extract = retrieval.extract
# The compiled candidate has its own globals; patch both explicit lookup tables.
for label, cls in [('current', retrieval.HelperRetrieval), ('candidate', candidate_class)]:
    owned = out / label
    source, journal = owned / 'source', owned / 'journal'
    source.mkdir(parents=True); journal.mkdir()
    (source / 'owned.go').write_bytes(raw)
    registry = {'owned': {'root': str(source), 'revision': 'd' * 40, 'files': {'owned.go': {'sha256': retrieval.sha(raw), 'language': 'go', 'selectors': ['Selected']}}}}
    request = {'request_id': 'cached', 'source_id': 'owned', 'revision': 'd' * 40, 'path': 'owned.go', 'qualified_symbol': 'Selected', 'expected_sha256': retrieval.sha(raw)}
    helper = cls(registry, str(journal))
    initial = helper.request(request)
    duplicate = helper.request(request)
    assert initial['status'] == 'FOUND' and duplicate['status'] == 'DUPLICATE'
    baseline = {f.name: retrieval.sha(f.read_bytes()) for f in journal.iterdir()}
    for fault_name, error in [('TimeoutExpired', subprocess.TimeoutExpired('owned-no-process', 20)), ('CalledProcessError', subprocess.CalledProcessError(2, 'owned-no-process'))]:
        def fault(*args, captured=error):
            raise captured
        retrieval.extract = fault; namespace['extract'] = fault
        try:
            result = helper.request(request)
            observed = {'status': result['status'], 'raised': None, 'quote_exposed': 'evidence' in result}
        except subprocess.SubprocessError as exc:
            observed = {'status': None, 'raised': type(exc).__name__, 'quote_exposed': False}
        finally:
            retrieval.extract = original_extract; namespace['extract'] = original_extract
        after = {f.name: retrieval.sha(f.read_bytes()) for f in journal.iterdir()}
        lock_released = helper._request_lock.acquire(blocking=False)
        if lock_released: helper._request_lock.release()
        assert baseline == after and lock_released
        if label == 'candidate': assert observed['status'] == 'REFUSED' and not observed['quote_exposed']
        else: assert observed['raised'] == fault_name
        rows.append({'implementation': label, 'fault': fault_name, 'observed': observed, 'journal_bytes_unchanged': baseline == after, 'lock_released': lock_released})
    recovered = helper.request(request)
    assert recovered['status'] == 'DUPLICATE'
files = [{'path': str(f.relative_to(out)), 'bytes': f.stat().st_size, 'sha256': retrieval.sha(f.read_bytes())} for f in sorted(out.rglob('*')) if f.is_file()]
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'ISOLATED_ERROR_DELIVERY_METHOD_CANDIDATE_OBSERVED_NOT_APPLIED', 'current_source_sha256': retrieval.sha(Path(retrieval.__file__).read_bytes()), 'current_source_version': retrieval.VERSION, 'change': 'Add subprocess.SubprocessError to the outer cached-request refusal handler. Research subclass only; no version bump or production file change.', 'native_baselines': 'Both implementations FOUND then DUPLICATE through existing native Go parser; after each fault series valid cached duplicate still succeeds.', 'rows': rows, 'scope': 'Two injected exception types on the same one owned callable; four observations are not independent accuracy cases. No actual process timeout, hung child, parser outage or source execution.', 'candidate_semantics': 'REFUSED with no quote and no journal rewrite/retry; adopting this status versus another operational status requires explicit API review.', 'owned_root': str(out), 'files': files, 'production_changed': False, 'permanent_tests_changed': False, 'model_calls': 0, 'optimizer_steps': 0, 'owner_gold': 0, 'training_excluded': True}
with (P / 'helper-timeout-delivery-candidate-v1.json').open('x') as stream:
    json.dump(record, stream, indent=2); stream.write('\n')
print(json.dumps({'observations': len(rows), 'candidate_both_faults_refused': True, 'native_found_duplicate_recovered': True, 'owned_files': len(files), 'production_changed': False}))
