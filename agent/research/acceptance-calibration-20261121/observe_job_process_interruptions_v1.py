"""Actual owned process stops and independent reopen; no helper replay."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parents[2]
protocol_path = P / 'job-process-interruption-protocol-v1.json'
protocol = json.loads(protocol_path.read_text())
for item in protocol['source_files']:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
sys.path.insert(0, str(ROOT / 'agent/tools'))
import documentation_job_budget as jobs

BASE = P / 'job-process-interruption-v1'
BASE.mkdir(exist_ok=False)
clock = lambda: datetime.datetime.fromisoformat(protocol['clock'])
expected_body = jobs.canonical(protocol['body'])
expected_sha = hashlib.sha256(expected_body).hexdigest()


def snapshot(folder):
    return {str(f.relative_to(folder)): {'bytes': f.stat().st_size,
            'sha256': hashlib.sha256(f.read_bytes()).hexdigest()}
            for f in sorted(folder.rglob('*')) if f.is_file()}


def reopen(folder):
    before = snapshot(folder)
    try:
        budget = jobs.HelperJobBudget(folder / 'job-journal', protocol['config'], clock=clock)
        result = budget.reserve(protocol['request'])
    except (jobs.JobRefused, ValueError, OSError) as error:
        result = {'status': 'REFUSED', 'reason': str(error)}
    body_path = folder / 'delivery/body.json'
    if not body_path.exists():
        delivery = 'MISSING_REFUSED'
        digest = None
    else:
        digest = hashlib.sha256(body_path.read_bytes()).hexdigest()
        delivery = 'VALID' if digest == expected_sha else 'HASH_MISMATCH_REFUSED'
    completion = result.get('completion')
    completion_matches = bool(completion and completion['result_sha256'] == digest == expected_sha)
    return {'budget_result': result, 'delivery_gate': delivery,
            'delivery_sha256': digest, 'expected_delivery_sha256': expected_sha,
            'completion_and_body_hash_match': completion_matches,
            'files_before_reopen': before, 'files_after_reopen': snapshot(folder),
            'helper_dispatches': 0, 'automatic_retries': 0}


records = []
for case in protocol['process_stops']:
    folder = BASE / case['id']
    (folder / 'job-journal').mkdir(parents=True)
    (folder / 'delivery').mkdir()
    command = [sys.executable, '-B', str(P / 'job_process_interruption_worker_v1.py'), case['id'], str(folder)]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    observed = subprocess.run(command, capture_output=True, timeout=20)
    (folder / 'worker.stdout').write_bytes(observed.stdout)
    (folder / 'worker.stderr').write_bytes(observed.stderr)
    assert observed.returncode == case['stop_exit_code'], (case, observed.stderr.decode())
    actual = reopen(folder)
    body_kind = 'NONE' if actual['delivery_sha256'] is None else 'VALID' if actual['delivery_gate'] == 'VALID' else 'PARTIAL'
    matches = actual['budget_result']['status'] == case['expected_reopen_status'] and body_kind == case['expected_delivery']
    row = {'id': case['id'], 'kind': 'ACTUAL_CHILD_PROCESS_ABRUPT_EXIT',
           'started_at': started, 'ended_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'command': command, 'actual_exit_code': observed.returncode,
           'expected': case, 'observation': actual, 'matches_frozen_reference': matches}
    with (folder / 'observation-v1.json').open('x') as stream:
        json.dump(row, stream, indent=2); stream.write('\n')
    records.append(row)

complete = BASE / 'after_completion'
for case in protocol['postcomplete_forks']:
    folder = BASE / case['id']
    folder.mkdir()
    shutil.copytree(complete / 'job-journal', folder / 'job-journal')
    (folder / 'delivery').mkdir()
    if case['id'] == 'completed_journal_tampered_body':
        with (folder / 'delivery/body.json').open('xb') as stream:
            stream.write(b'{"status":"FOUND","owned_tampered_copy":true}')
    actual = reopen(folder)
    matches = actual['budget_result']['status'] == case['expected_budget_status'] and actual['delivery_gate'] == case['expected_delivery_gate']
    row = {'id': case['id'], 'kind': 'NONDESTRUCTIVE_COMPLETED_JOURNAL_FORK',
           'original_completed_case_preserved': True, 'expected': case,
           'observation': actual, 'matches_frozen_reference': matches}
    with (folder / 'observation-v1.json').open('x') as stream:
        json.dump(row, stream, indent=2); stream.write('\n')
    records.append(row)

for item in protocol['source_files']:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'protocol': protocol_path.name,
          'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
          'records': records, 'actual_process_stops': 8, 'non_destructive_forks': 2,
          'matches': sum(r['matches_frozen_reference'] for r in records), 'cases': len(records),
          'interpretation': 'Direct exclusive-create publication can retain partial config/reservation/completion after abrupt process exit; current reopening safely refuses those journals. A fully persisted payload before completion remains UNKNOWN_COMPLETION, not automatically replayable/completed. Completed metadata alone still reports DUPLICATE_COMPLETED when a fork has missing/tampered delivery bytes; separate exact body verification refuses delivery. No caught fault, pending receipt or completion hash alone proves durable deliverability.',
          'limitations': protocol['limits'], 'real_helper_or_source_execution': False,
          'production_source_hashes_unchanged': True, 'permanent_tests_added': False,
          'model_calls': 0, 'optimizer_updates': 0, 'gold': 0}
with (P / 'job-process-interruption-results-v1.json').open('x') as stream:
    json.dump(result, stream, indent=2); stream.write('\n')
print(json.dumps({'matches': result['matches'], 'cases': len(records),
                  'observed': [(r['id'], r['observation']['budget_result']['status'],
                                r['observation']['delivery_gate']) for r in records]}, indent=2))
