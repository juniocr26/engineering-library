"""Owned bounded fault/concurrency observations, never a permanent test suite."""
import datetime
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import textwrap
import threading

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[2] / 'agent/tools'))
import documentation_retrieval as retrieval

protocol = json.loads((P / 'helper-timeout-concurrency-protocol-v1.json').read_text())
assert retrieval.sha(Path(retrieval.__file__).read_bytes()) == protocol['baseline_sha256']
out = P / 'helper-timeout-concurrency-owned-v1'
out.mkdir(exist_ok=False)
original = textwrap.dedent(inspect.getsource(retrieval.HelperRetrieval._request))
old = 'except (RetrievalRefused, WorkspaceRefused, ValueError, OSError, UnicodeError, KeyError, TypeError, RecursionError) as error:'
new = old.replace('RecursionError)', 'RecursionError, subprocess.SubprocessError)')
assert original.count(old) == 1
candidate = original.replace(old, new)
(out / 'original-method.py').write_text(original)
(out / 'candidate-method.py').write_text(candidate)
namespace = dict(retrieval.__dict__)
exec(compile(candidate, '<owned-prior-handler-candidate>', 'exec'), namespace)
candidate_class = type('OwnedPriorHandlerCandidate', (retrieval.HelperRetrieval,), {'_request': namespace['_request']})
original_extract = retrieval.extract
raw = b'package owned\n\nfunc Selected() int { return 7 }\n'
rows = []


def journal_snapshot(path):
    return {f.name: retrieval.sha(f.read_bytes()) for f in sorted(path.iterdir()) if f.is_file()}


for implementation, cls in [('current', retrieval.HelperRetrieval), ('prior-isolated-handler-candidate', candidate_class)]:
    for phase in ['cached-success-revalidation', 'fresh-extraction']:
        for fault_name in ['TimeoutExpired', 'CalledProcessError']:
            label = implementation + '-' + phase + '-' + fault_name
            owned = out / label
            source, journal = owned / 'source', owned / 'journal'
            source.mkdir(parents=True)
            journal.mkdir()
            (source / 'owned.go').write_bytes(raw)
            registry = {'owned': {'root': str(source), 'revision': 'e' * 40,
                                  'files': {'owned.go': {'sha256': retrieval.sha(raw), 'language': 'go', 'selectors': ['Selected']}}}}
            request = {'request_id': 'selected', 'source_id': 'owned', 'revision': 'e' * 40,
                       'path': 'owned.go', 'qualified_symbol': 'Selected', 'expected_sha256': retrieval.sha(raw)}
            helper = cls(registry, str(journal))
            initial = None
            if phase == 'cached-success-revalidation':
                initial = helper.request(request)
                assert initial['status'] == 'FOUND'
            before = journal_snapshot(journal)
            budgets_before = {'steps': helper.steps, 'quote_bytes': helper.quote_bytes}
            entered, release = threading.Event(), threading.Event()
            fault_calls = []
            delivered = {}

            def fault(*args):
                fault_calls.append({'selector': args[1], 'language': args[2]})
                entered.set()
                assert release.wait(5), 'owned handshake release deadline exceeded'
                if fault_name == 'TimeoutExpired':
                    raise subprocess.TimeoutExpired('owned-no-child-process', 20)
                raise subprocess.CalledProcessError(2, 'owned-no-child-process')

            def request_worker():
                try:
                    delivered['response'] = helper.request(request)
                    delivered['raised'] = None
                except BaseException as error:
                    delivered['response'] = None
                    delivered['raised'] = type(error).__name__

            retrieval.extract = fault
            namespace['extract'] = fault
            worker = threading.Thread(target=request_worker, daemon=True)
            try:
                worker.start()
                assert entered.wait(5), 'owned worker never entered extraction'
                during = journal_snapshot(journal)
                concurrent = helper.request(request)
                after_concurrent = journal_snapshot(journal)
                assert concurrent['status'] == 'IN_PROGRESS_OR_INTERRUPTED'
                assert during == after_concurrent and len(fault_calls) == 1
            finally:
                release.set()
                worker.join(5)
                retrieval.extract = original_extract
                namespace['extract'] = original_extract
            assert not worker.is_alive(), 'owned worker still active after bounded join'
            after = journal_snapshot(journal)
            unlocked = helper._request_lock.acquire(blocking=False)
            assert unlocked
            helper._request_lock.release()
            budgets_after = {'steps': helper.steps, 'quote_bytes': helper.quote_bytes}
            if phase == 'cached-success-revalidation':
                assert before == during == after and budgets_before == budgets_after
                if implementation == 'current':
                    assert delivered['raised'] == fault_name
                else:
                    assert delivered['raised'] is None and delivered['response']['status'] == 'REFUSED'
                    assert 'evidence' not in delivered['response']
                expected_original = 'FOUND'
            else:
                assert delivered['raised'] is None and delivered['response']['status'] == 'INCONCLUSIVE'
                assert set(during) == {'selected.request.json'}
                assert set(after) == {'selected.request.json', 'selected.result.json', 'selected.receipt.json'}
                assert helper.steps == 1 and helper.quote_bytes == 0
                expected_original = 'INCONCLUSIVE'
            recovery_extract_calls = []

            def count_extract(*args):
                recovery_extract_calls.append({'selector': args[1], 'language': args[2]})
                return original_extract(*args)

            retrieval.extract = count_extract
            namespace['extract'] = count_extract
            try:
                recovered = helper.request(request)
                calls_after_same_id = len(recovery_extract_calls)
                assert recovered['status'] == 'DUPLICATE' and recovered['original_status'] == expected_original
                assert 'evidence' not in recovered and journal_snapshot(journal) == after
                if phase == 'fresh-extraction':
                    assert calls_after_same_id == 0
                    new_request = helper.request({**request, 'request_id': 'new-attempt'})
                    assert new_request['status'] == 'FOUND' and helper.steps == 2
                else:
                    new_request = None
            finally:
                retrieval.extract = original_extract
                namespace['extract'] = original_extract
            rows.append({'id': label, 'implementation': implementation, 'phase': phase, 'fault': fault_name,
                         'initial': initial, 'delivery': delivered, 'concurrent': concurrent,
                         'journal_before': before, 'journal_during_fault': during, 'journal_after_concurrent': after_concurrent,
                         'journal_after_fault': after, 'budgets_before': budgets_before, 'budgets_after_fault': budgets_after,
                         'lock_released': unlocked, 'fault_extract_calls': len(fault_calls),
                         'same_id_recovery': recovered, 'same_id_recovery_extract_calls': calls_after_same_id,
                         'new_id_recovery': new_request, 'all_declared_invariants_matched': True})

assert len(rows) == protocol['scenario_count']
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'protocol': 'helper-timeout-concurrency-protocol-v1.json',
          'rows': rows, 'matched': len(rows), 'total': len(rows),
          'production_source_sha256': retrieval.sha(Path(retrieval.__file__).read_bytes()),
          'production_unchanged': True, 'source_program_executed': False, 'permanent_tests_changed': False,
          'actual_hung_child_or_outage': False, 'fault_scope': 'Owned in-process fault and event handshake only; not OS process cancellation or cross-process locking certification.',
          'api_limit': 'Prior isolated candidate delivers cached faults as REFUSED while fresh faults persist INCONCLUSIVE. Uniform caller semantics remain an explicit future API decision, not applied here.',
          'model_calls': 0, 'training_gold': False,
          'owned_files': [{'path': str(f.relative_to(out)), 'bytes': f.stat().st_size, 'sha256': retrieval.sha(f.read_bytes())}
                          for f in sorted(out.rglob('*')) if f.is_file()]}
assert record['production_source_sha256'] == protocol['baseline_sha256']
with (P / 'helper-timeout-concurrency-observation-v1.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'matched': len(rows), 'total': len(rows), 'owned_files': len(record['owned_files']),
                  'production_unchanged': True, 'source_program_executed': False}))
