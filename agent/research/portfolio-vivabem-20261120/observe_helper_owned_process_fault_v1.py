"""Observe real owned child failures behind an isolated extraction replacement."""
import datetime
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import time

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[2] / 'agent/tools'))
import documentation_retrieval as retrieval

protocol = json.loads((P / 'helper-owned-process-fault-protocol-v1.json').read_text())
assert retrieval.sha(Path(retrieval.__file__).read_bytes()) == protocol['baseline_sha256']
out = P / 'helper-owned-process-fault-artifacts-v1'
out.mkdir(exist_ok=False)
original_source = textwrap.dedent(inspect.getsource(retrieval.HelperRetrieval._request))
old = 'except (RetrievalRefused, WorkspaceRefused, ValueError, OSError, UnicodeError, KeyError, TypeError, RecursionError) as error:'
assert original_source.count(old) == 1
candidate_source = original_source.replace(old, old.replace('RecursionError)', 'RecursionError, subprocess.SubprocessError)'))
(out / 'original-method.py').write_text(original_source)
(out / 'candidate-method.py').write_text(candidate_source)
namespace = dict(retrieval.__dict__)
exec(compile(candidate_source, '<owned-research-handler-candidate>', 'exec'), namespace)
candidate_class = type('OwnedProcessHandlerCandidate', (retrieval.HelperRetrieval,), {'_request': namespace['_request']})
child_code = '''import json, os, sys, time
mode = sys.argv[1]
print(json.dumps({'owned_child_pid': os.getpid(), 'mode': mode}), flush=True)
if mode == 'owned-timeout':
    time.sleep(5)
    raise SystemExit(99)
raise SystemExit(7)
'''
(out / 'owned-child-source.py').write_text(child_code)
raw = b'package owned\n\nfunc Selected() int { return 7 }\n'
original_extract = retrieval.extract
rows = []


def snapshot(path):
    return {f.name: retrieval.sha(f.read_bytes()) for f in sorted(path.iterdir()) if f.is_file()}


for implementation, cls in [('current', retrieval.HelperRetrieval), ('prior-isolated-handler-candidate', candidate_class)]:
    for phase in ['cached', 'fresh']:
        for mode in ['owned-timeout', 'owned-nonzero-exit']:
            label = implementation + '-' + phase + '-' + mode
            owned = out / label
            source, journal = owned / 'source', owned / 'journal'
            source.mkdir(parents=True)
            journal.mkdir()
            (source / 'owned.go').write_bytes(raw)
            registry = {'owned': {'root': str(source), 'revision': 'f' * 40,
                                  'files': {'owned.go': {'sha256': retrieval.sha(raw), 'language': 'go', 'selectors': ['Selected']}}}}
            request = {'request_id': 'selected', 'source_id': 'owned', 'revision': 'f' * 40,
                       'path': 'owned.go', 'qualified_symbol': 'Selected', 'expected_sha256': retrieval.sha(raw)}
            helper = cls(registry, str(journal))
            if phase == 'cached':
                assert helper.request(request)['status'] == 'FOUND'
            before = snapshot(journal)
            budget_before = {'steps': helper.steps, 'quote_bytes': helper.quote_bytes}
            child_observations = []

            def actual_owned_child(*args):
                started = time.monotonic()
                try:
                    subprocess.run([sys.executable, '-I', '-S', '-c', child_code, mode],
                                   cwd=owned, env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1'},
                                   capture_output=True, check=True, timeout=0.25)
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as error:
                    output = error.stdout or b''
                    assert len(output) <= 1024
                    marker = json.loads(output)
                    assert marker['mode'] == mode and type(marker['owned_child_pid']) is int
                    pid = marker['owned_child_pid']
                    try:
                        os.kill(pid, 0)
                    except ProcessLookupError:
                        absent = True
                    else:
                        absent = False
                    assert absent, 'owned child PID still exists after subprocess cleanup'
                    expected = 'TimeoutExpired' if mode == 'owned-timeout' else 'CalledProcessError'
                    assert type(error).__name__ == expected
                    if mode == 'owned-nonzero-exit':
                        assert error.returncode == 7
                    child_observations.append({'pid': pid, 'mode': mode, 'exception': type(error).__name__,
                                               'returncode': getattr(error, 'returncode', None),
                                               'child_pid_absent_after_cleanup': absent,
                                               'wall_seconds': time.monotonic() - started,
                                               'owned_marker': marker, 'stderr_bytes': len(error.stderr or b'')})
                    raise
                raise AssertionError('owned fault child unexpectedly succeeded')

            retrieval.extract = actual_owned_child
            namespace['extract'] = actual_owned_child
            try:
                try:
                    response = helper.request(request)
                    delivery = {'raised': None, 'response': response}
                except subprocess.SubprocessError as error:
                    delivery = {'raised': type(error).__name__, 'response': None}
            finally:
                retrieval.extract = original_extract
                namespace['extract'] = original_extract
            assert len(child_observations) == 1
            after = snapshot(journal)
            budget_after = {'steps': helper.steps, 'quote_bytes': helper.quote_bytes}
            unlocked = helper._request_lock.acquire(blocking=False)
            assert unlocked
            helper._request_lock.release()
            if phase == 'cached':
                assert before == after and budget_before == budget_after
                if implementation == 'current':
                    assert delivery['raised'] == child_observations[0]['exception']
                else:
                    assert delivery['raised'] is None and delivery['response']['status'] == 'REFUSED'
                    assert 'evidence' not in delivery['response']
                original_status = 'FOUND'
            else:
                assert delivery['raised'] is None and delivery['response']['status'] == 'INCONCLUSIVE'
                assert set(after) == {'selected.request.json', 'selected.result.json', 'selected.receipt.json'}
                original_status = 'INCONCLUSIVE'
            recovered = helper.request(request)
            assert recovered['status'] == 'DUPLICATE' and recovered['original_status'] == original_status
            assert 'evidence' not in recovered and snapshot(journal) == after
            if phase == 'fresh':
                new_attempt = helper.request({**request, 'request_id': 'new-attempt'})
                assert new_attempt['status'] == 'FOUND'
            else:
                new_attempt = None
            rows.append({'id': label, 'implementation': implementation, 'phase': phase, 'mode': mode,
                         'child': child_observations[0], 'delivery': delivery, 'lock_released': unlocked,
                         'journal_before': before, 'journal_after': after,
                         'budget_before': budget_before, 'budget_after_fault': budget_after,
                         'same_id_recovery': recovered, 'new_id_recovery': new_attempt,
                         'all_declared_invariants_matched': True})

assert len(rows) == protocol['scenario_count']
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'protocol': 'helper-owned-process-fault-protocol-v1.json', 'rows': rows,
          'matched': len(rows), 'total': len(rows), 'actual_owned_children': len(rows),
          'all_owned_child_pids_absent': all(r['child']['child_pid_absent_after_cleanup'] for r in rows),
          'scope': 'Owned replacement extractor uses real subprocess.run child timeout/exit; native parser itself was not hung or faulted.',
          'production_sha256': retrieval.sha(Path(retrieval.__file__).read_bytes()),
          'source_program_executed': False, 'owned_fault_program_executed': True,
          'external_repository_writes': 0, 'permanent_tests_changed': False, 'production_changed': False,
          'model_calls': 0, 'training_gold': False,
          'files': [{'path': str(f.relative_to(out)), 'bytes': f.stat().st_size, 'sha256': retrieval.sha(f.read_bytes())}
                    for f in sorted(out.rglob('*')) if f.is_file()]}
assert record['production_sha256'] == protocol['baseline_sha256']
with (P / 'helper-owned-process-fault-observation-v1.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'matched': len(rows), 'total': len(rows), 'all_owned_child_pids_absent': record['all_owned_child_pids_absent'],
                  'owned_files': len(record['files']), 'child_wall_seconds': sum(r['child']['wall_seconds'] for r in rows),
                  'production_changed': False}))
