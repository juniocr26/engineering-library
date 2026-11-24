"""Owned optional helper/job adapter integration; no Ruby/application execution."""
import datetime
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
import documentation_job_budget as jobs

protocol = json.loads((P / 'helper-job-delivery-integration-protocol-v1.json').read_text())
for path, digest in protocol['source_hashes'].items():
    assert retrieval.sha((ROOT / path).read_bytes()) == digest
out = P / 'helper-job-delivery-owned-v1'
out.mkdir(exist_ok=False)
original_source = textwrap.dedent(inspect.getsource(retrieval.HelperRetrieval._request))
old = 'except (RetrievalRefused, WorkspaceRefused, ValueError, OSError, UnicodeError, KeyError, TypeError, RecursionError) as error:'
assert original_source.count(old) == 1
candidate_source = original_source.replace(old, old.replace('RecursionError)', 'RecursionError, subprocess.SubprocessError)'))
(out / 'original-method.py').write_text(original_source)
(out / 'candidate-method.py').write_text(candidate_source)
namespace = dict(retrieval.__dict__)
exec(compile(candidate_source, '<owned-optional-job-handler-candidate>', 'exec'), namespace)
candidate_class = type('OwnedJobHandlerCandidate', (retrieval.HelperRetrieval,), {'_request': namespace['_request']})
original_extract = retrieval.extract
raw = b'package owned\n\nfunc Selected() int { return 7 }\n'
fixed_now = datetime.datetime.now(datetime.timezone.utc)
rows = []


def snapshot(path):
    return {f.name: retrieval.sha(f.read_bytes()) for f in sorted(path.iterdir()) if f.is_file()}


for implementation, cls in [('current', retrieval.HelperRetrieval), ('prior-isolated-handler-candidate', candidate_class)]:
    for phase in ['cached', 'fresh']:
        owned = out / (implementation + '-' + phase)
        source, journal, job_root = owned / 'source', owned / 'helper-journal', owned / 'job-journal'
        source.mkdir(parents=True)
        journal.mkdir()
        job_root.mkdir()
        (source / 'owned.go').write_bytes(raw)
        registry = {'owned': {'root': str(source), 'revision': 'a' * 40,
                              'files': {'owned.go': {'sha256': retrieval.sha(raw), 'language': 'go', 'selectors': ['Selected']}}}}
        request = {'request_id': 'selected', 'source_id': 'owned', 'revision': 'a' * 40,
                   'path': 'owned.go', 'qualified_symbol': 'Selected', 'expected_sha256': retrieval.sha(raw)}
        helper = cls(registry, str(journal))
        if phase == 'cached':
            assert helper.request(request)['status'] == 'FOUND'
        config = {'job_id': 'owned-integration', 'registry_sha256': helper.registry_sha256,
                  'max_steps': 4, 'max_quote_bytes': 24576,
                  'deadline_utc': (fixed_now + datetime.timedelta(hours=1)).isoformat()}
        budget = jobs.HelperJobBudget(job_root, config, clock=lambda: fixed_now)
        adapter = jobs.JobBoundRetrieval(helper, budget)
        helper_before, job_before = snapshot(journal), snapshot(job_root)
        fault_calls = []

        def fault(*args):
            fault_calls.append({'selector': args[1], 'language': args[2]})
            raise subprocess.TimeoutExpired('owned-integration-no-process-started', 20)

        retrieval.extract = fault
        namespace['extract'] = fault
        try:
            response = adapter.request(request)
            assert len(fault_calls) == 1
            helper_after, job_after = snapshot(journal), snapshot(job_root)
            repeat = adapter.request(request)
            assert len(fault_calls) == 1
            assert snapshot(journal) == helper_after and snapshot(job_root) == job_after
        finally:
            retrieval.extract = original_extract
            namespace['extract'] = original_extract
        if phase == 'cached' and implementation == 'current':
            assert response['status'] == repeat['status'] == 'UNKNOWN_COMPLETION'
            assert 'step-0001-reserved.json' in job_after and 'step-0001-completed.json' not in job_after
            expected_result_status = None
        else:
            assert response['status'] == 'COMPLETED' and repeat['status'] == 'DUPLICATE_COMPLETED'
            expected_result_status = 'REFUSED' if phase == 'cached' else 'INCONCLUSIVE'
            assert response['job_completion']['result_status'] == expected_result_status
            assert response['helper_result']['status'] == expected_result_status
            assert 'evidence' not in response['helper_result']
            assert 'step-0001-completed.json' in job_after
        if phase == 'cached':
            assert helper_before == helper_after
        else:
            assert {'selected.request.json', 'selected.result.json', 'selected.receipt.json'} == set(helper_after)
        unlocked = helper._request_lock.acquire(blocking=False)
        assert unlocked
        helper._request_lock.release()
        rows.append({'implementation': implementation, 'phase': phase, 'response': response, 'repeat_response': repeat,
                     'helper_journal_before': helper_before, 'helper_journal_after_fault': helper_after,
                     'job_journal_before': job_before, 'job_journal_after_fault': job_after,
                     'same_id_repeat_no_dispatch_or_journal_write': True, 'fault_extract_calls': len(fault_calls),
                     'job_completed_result_status': expected_result_status, 'helper_lock_released': unlocked,
                     'all_declared_invariants_matched': True})

assert len(rows) == protocol['cases']
for path, digest in protocol['source_hashes'].items():
    assert retrieval.sha((ROOT / path).read_bytes()) == digest
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'protocol': 'helper-job-delivery-integration-protocol-v1.json', 'matched': len(rows), 'total': len(rows), 'rows': rows,
          'semantics': 'COMPLETED means accounted helper terminal response, not successful source retrieval. UNKNOWN_COMPLETION preserves unresolved job reservation without replay.',
          'scope': 'Owned HelperRetrieval/HelperJobBudget/JobBoundRetrieval integration with injected timeout; not Ruby command or deployment integration.',
          'source_program_executed': False, 'production_changed': False, 'permanent_tests_changed': False,
          'files': [{'path': str(f.relative_to(out)), 'bytes': f.stat().st_size, 'sha256': retrieval.sha(f.read_bytes())}
                    for f in sorted(out.rglob('*')) if f.is_file()]}
with (P / 'helper-job-delivery-integration-observation-v1.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'matched': len(rows), 'total': len(rows), 'statuses': [r['response']['status'] for r in rows],
                  'owned_files': len(record['files']), 'production_changed': False}))
