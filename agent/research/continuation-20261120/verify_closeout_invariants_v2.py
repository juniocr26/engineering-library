"""Read-only whole-source, frozen-data, request and quarantine closeout audit."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
baseline = json.loads((P / 'baseline.json').read_text())

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): digest.update(block)
    return digest.hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, env=env)

modified_allowed = {'backend/lib/documentation/command.rb', 'backend/lib/documentation/python_structure.py',
                    'agent/tools/documentation_retrieval.py', 'agent/recovery/manifest.json'}
deleted_allowed = {'agent/research/documentation-intelligence-20261120/' + name for name in
                   ['CAMPAIGN_REPORT.md', 'FILE_INVENTORY.md', 'FIRST_NEURAL_FINE_TUNING_READINESS.md', 'PROGRESS.md', 'RESUME.md']}
unchanged, modified, deleted = [], [], []
for name, identity in baseline['tracked_identity'].items():
    path = ROOT / name
    if name in deleted_allowed:
        assert not path.exists(), name
        deleted.append(name)
    else:
        actual = sha(path)
        if actual == identity['sha256']: unchanged.append(name)
        else:
            assert name in modified_allowed, 'unexpected tracked drift: ' + name
            modified.append({'path': name, 'baseline_sha256': identity['sha256'], 'current_sha256': actual})
assert {row['path'] for row in modified} == modified_allowed
assert git('rev-parse', 'HEAD').decode().strip() == baseline['head']
assert sha(ROOT / '.git/index') == baseline['index_sha256']
assert 'mode change' not in git('diff', '--summary').decode()
canonical = {'AI_TRAINING_CAMPAIGN_REPORT.md', 'AI_TRAINING_FILE_INVENTORY.md', 'AI_FINE_TUNING_READINESS.md', 'AI_TRAINING_RESUME.md'}
status = []
for value in git('status', '--porcelain=v1', '-z', '--untracked-files=all').split(b'\0'):
    if not value: continue
    item = value.decode(); flag, name = item[:2], item[3:]
    if flag == '??': assert name in canonical or name.startswith('agent/research/continuation-20261120/'), name
    elif flag.strip() == 'M': assert name in modified_allowed, name
    elif flag.strip() == 'D': assert name in deleted_allowed, name
    else: raise ValueError('unexpected Git status: ' + item)
    status.append({'status': flag, 'path': name})
current = json.loads((ROOT / 'agent/recovery/manifest.json').read_text())
old = json.loads(git('show', baseline['head'] + ':agent/recovery/manifest.json'))
assert current['model'] == old['model'] and current['runtime'] == old['runtime']
pins = {row['path']: row for row in current['operational_files']}
assert len(pins) == len(current['operational_files']) == 1964
for name in modified_allowed - {'agent/recovery/manifest.json'}:
    assert sha(ROOT / name) == pins[name]['sha256']
normal = json.loads((P / 'operational-manifest-go-history-completion-v1.json').read_text())
assert normal['current_manifest_sha256'] == sha(ROOT / 'agent/recovery/manifest.json')
assert normal['bootstrap']['status'] == 'verified'

lineage = json.loads((P / 'dataset-lineage-audit-v1.json').read_text())
dataset_files, ids, flags = [], [], collections.Counter()
for row in lineage['file_checks']:
    path = ROOT / row['path']; assert sha(path) == row['sha256']
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(records) == row['records']
    for record in records:
        ids.append(record['id'])
        for flag in ['owner_approved', 'training_gold', 'training_use_approved']:
            assert record.get(flag) is not True
            flags[flag + ':' + ('false' if record.get(flag) is False else 'missing-or-other-unapproved')] += 1
    dataset_files.append({'path': row['path'], 'sha256': row['sha256'], 'records': len(records)})
assert len(ids) == len(set(ids)) == 305

summary = json.loads((P / 'current-model-call-summary-v8.json').read_text())
requests, tokens, seconds = [], 0, 0.0
for row in summary['records']:
    folder = P / row['folder']
    request = json.loads((folder / 'request.json').read_text())
    payload = json.dumps(request, ensure_ascii=False).encode()
    dispatch = json.loads((folder / 'dispatch.json').read_text())
    response = json.loads((folder / 'response.json').read_text())
    assert hashlib.sha256(payload).hexdigest() == dispatch['request_sha256']
    if 'bytes' in dispatch: assert len(payload) == dispatch['bytes']
    assert sha(folder / 'response.json') == row['raw_response_sha256']
    assert response['done'] is True and response['model'] == summary['same_model']
    assert request['model'] == summary['same_model'] == current['model']['name']
    assert row['review_status'].startswith('REJECTED') or row['review_status'] == 'STRICT_FULL_COPY_OUTPUT_REJECTED_PARTIAL_ENGLISH_QUOTED_STRING_DIAGNOSTIC_ONLY', row['folder']
    tokens += response['eval_count']; seconds += response['total_duration'] / 1e9
    requests.append({'folder': row['folder'], 'request_sha256': dispatch['request_sha256'],
                     'recorded_length_verified': 'bytes' in dispatch, 'done': response['done'],
                     'raw_response_sha256': row['raw_response_sha256'], 'review_status': row['review_status'],
                     'generated_tokens': response['eval_count'], 'server_seconds': response['total_duration'] / 1e9})
assert len(requests) == summary['new_calls_this_continuation'] == 9
assert tokens == summary['completed_generated_tokens'] == 8140
assert abs(seconds - summary['completed_server_seconds']) < 1e-6
assert summary['active_model_calls'] == summary['strict_complete_outputs_accepted'] == summary['optimizer_steps'] == summary['gold'] == 0
exclusions = []
for number in range(2, 12):
    path = P / ('training-exclusion-registry-supplement-v' + str(number) + '.json')
    value = json.loads(path.read_text())
    if number > 2: assert value['extends'] == 'training-exclusion-registry-supplement-v' + str(number - 1) + '.json'
    exclusions.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path)})
assert value['default_deny_unreviewed_derivatives'] is True
faq = json.loads((P / 'faq-identity-overlap-audit-v8.json').read_text())
assert faq['frozen_V10_question_pairs'] == 77 and faq['current_candidate_pairs'] == 66
assert faq['current_chapter_derived_pairs'] == 60 and faq['current_standalone_pairs'] == 6
assert not faq['current_code_span_differences'] and faq['all_owner_and_training_flags_false'] is True
index = json.loads((P / 'current-documentation-candidate-index-v1.json').read_text())
assert (index['candidate_chapters'], index['source_reviewed_claims'], index['physical_source_units_bound']) == (9, 113, 255)
consumption = json.loads((P / 'current-candidate-index-consumption-v1.json').read_text())
assert consumption['index_sha256'] == sha(P / 'current-documentation-candidate-index-v1.json')
assert consumption['reader_and_workspace_loaded_from_selected_root'] is True
location = json.loads((P / 'markdown-report-location-followup-v3.json').read_text())
assert location['no_new_nested_live_campaign_reports_found'] is True and not location['requires_review']
now = datetime.datetime.now(datetime.timezone.utc)
result = {'at': now.isoformat(), 'status': 'PRE_CLOSEOUT_INVARIANTS_PASS_NOT_DURATION_COMPLETION',
    'elapsed_hours': (now - datetime.datetime.fromisoformat(baseline['start_utc'])).total_seconds() / 3600,
    'duration_minimum_reached': now >= datetime.datetime.fromisoformat(baseline['minimum_target_utc']),
    'baseline_head': baseline['head'], 'head_unchanged': True, 'index_sha256': baseline['index_sha256'], 'index_unchanged': True,
    'unchanged_tracked_files': len(unchanged), 'modified_tracked_files': modified, 'deleted_tracked_report_copies': deleted,
    'tracked_modes_unchanged': True, 'untracked_paths_within_authorized_scope': True,
    'git_status_counts': dict(collections.Counter(row['status'] for row in status)),
    'manifest_sha256': sha(ROOT / 'agent/recovery/manifest.json'), 'operational_entries': 1964,
    'model_object_unchanged_from_owner_baseline': True, 'runtime_metadata_unchanged_from_owner_baseline': True,
    'source_runtime_boundary': {'working_caller_source_version': '1.9.43', 'working_helper_source_version': '0.1.5',
        'inherited_runtime_metadata_caller_version': current['runtime']['caller_version'],
        'verified_Ollama_version': current['runtime']['ollama_version'],
        'already_loaded_Rails_caller_version_measured': False, 'service_restarted': False},
    'dataset_files': dataset_files, 'dataset_records': 305, 'approval_flag_counts': dict(flags),
    'requests': requests, 'inference_calls_complete': 9, 'active_inference_calls': 0,
    'generated_tokens': tokens, 'server_seconds': seconds, 'explicit_dispatch_lengths_verified': sum(row['recorded_length_verified'] for row in requests),
    'legacy_missing_length_not_invented': True, 'all_nine_full_requested_outputs_rejected': True,
    'exclusion_chain': exclusions, 'default_deny_unreviewed_derivatives': True,
    'owner_gold': 0, 'optimizer_steps': 0, 'new_permanent_tests': 0, 'source_files_changed_by_audit': False,
    'limits': 'Whole tracked-byte/index/source-pin and recorded artifact integrity, not pristine-head test replay, independent semantic accuracy, already-loaded application version, cold boot or remote durability.'}
with (P / 'final-evidence-integrity-v1.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({key: result[key] for key in ['status', 'elapsed_hours', 'unchanged_tracked_files', 'git_status_counts', 'dataset_records', 'inference_calls_complete', 'generated_tokens', 'server_seconds', 'explicit_dispatch_lengths_verified']}))
