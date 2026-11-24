"""Seal post-source-cut reports/metadata without recursive archive or self-hash claims."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import tarfile
import time
from zoneinfo import ZoneInfo

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
OUT = ROOT / '.local-backups/continuation-20261120/final-root-envelope-v1'
ARCHIVE = OUT / 'root-reports-and-closing-metadata.tar.gz'
ENVELOPE_RECEIPT = OUT / 'receipt.json'
CLOSING = P / 'closing-receipt-v1.json'
SNAPSHOT = P / 'file-inventory-snapshot-v7.json'
REPORTS = ['AI_TRAINING_CAMPAIGN_REPORT.md', 'AI_TRAINING_FILE_INVENTORY.md', 'AI_FINE_TUNING_READINESS.md', 'AI_TRAINING_RESUME.md']

def now(): return datetime.datetime.now(datetime.timezone.utc)
def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): digest.update(block)
    return digest.hexdigest()
def write_new(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
def fill_pending(path, value):
    old = json.loads(path.read_text())
    assert old['status'] == 'PENDING_FINAL_CLOSEOUT_CONTROL', path
    with path.open('w') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())

parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['reserve', 'finalize'])
args = parser.parse_args()
baseline = json.loads((P / 'baseline.json').read_text())
start = datetime.datetime.fromisoformat(baseline['start_utc'])
minimum = datetime.datetime.fromisoformat(baseline['minimum_target_utc'])
assert minimum - start == datetime.timedelta(hours=11)
if now() < minimum: raise SystemExit('Final envelope refused before measured eleven-hour minimum')

if args.action == 'reserve':
    assert (P / 'recovery-delta-receipt-v7.json').is_file()
    OUT.mkdir(exist_ok=False)
    pending = {'at': now().isoformat(), 'status': 'PENDING_FINAL_CLOSEOUT_CONTROL',
               'no_completion_or_archive_identity_claimed': True}
    with ARCHIVE.open('xb'): pass
    write_new(ENVELOPE_RECEIPT, pending)
    write_new(CLOSING, pending)
    print(json.dumps({'status': 'THREE_OWNED_LATE_CONTROL_PATHS_RESERVED', 'pending_identity_not_final': True}))
    raise SystemExit(0)

started = time.monotonic()
assert ARCHIVE.is_file() and not ARCHIVE.is_symlink() and ARCHIVE.stat().st_size == 0
assert json.loads(CLOSING.read_text())['status'] == 'PENDING_FINAL_CLOSEOUT_CONTROL'
assert json.loads(ENVELOPE_RECEIPT.read_text())['status'] == 'PENDING_FINAL_CLOSEOUT_CONTROL'
cut_path = P / 'recovery-delta-receipt-v7.json'
cut = json.loads(cut_path.read_text())
assert cut['eleven_hours_claimed'] is True and cut['elapsed_seconds_at_receipt'] >= 11 * 3600
assert sha(ROOT / cut['delta_archive']['path']) == cut['delta_archive']['sha256']
input_path = ROOT / cut['input_manifest']['path']
assert sha(input_path) == cut['input_manifest']['sha256']
expected = json.loads(input_path.read_text())['effective_expected_files']
restore = Path(cut['restored_root']).resolve()
assert restore.parent == Path('/private/tmp') and restore.name == 'el-engineering-library-continuation-20261120-cut-v7-restore'
assert restore != ROOT.resolve()
consumption_path = P / 'final-candidate-index-restored-v7.json'
consumption = json.loads(consumption_path.read_text())
assert consumption['reader_and_workspace_loaded_from_selected_root'] is True
assert (consumption['candidate_chapters'], consumption['language_documents'], consumption['physical_source_cards']) == (9, 18, 255)
assert Path(consumption['root']).resolve() == restore
snapshot = json.loads(SNAPSHOT.read_text())
assert snapshot['eleven_hours_claimed'] is True
assert snapshot['modified_count'] == 4 and snapshot['deleted_count'] == 5
for path in [CLOSING, ARCHIVE, ENVELOPE_RECEIPT]:
    assert str(path.relative_to(ROOT)) in snapshot['late_generated_control_paths']
handoff = json.loads((P / 'root-handoff-final-v4.json').read_text())
assert handoff['duration_minimum_reached'] is True and handoff['eleven_hours_claimed'] is True
source_index = ROOT / 'agent/recovery/manifest.json'
evidence = json.loads((P / 'final-evidence-integrity-v1.json').read_text())
assert sha(source_index) == evidence['manifest_sha256']
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, env=env, text=True).strip()
assert head == baseline['head'] and sha(ROOT / '.git/index') == baseline['index_sha256']

selected = {ROOT / name for name in REPORTS}
for directory in [P, ROOT / '.local-backups/continuation-20261120']:
    for path in directory.rglob('*'):
        if not path.is_file() or path.is_symlink() or '__pycache__' in path.parts:
            continue
        if path == CLOSING or path.is_relative_to(OUT) or path == ROOT / cut['delta_archive']['path']:
            continue
        selected.add(path)
entries = []
for path in sorted(selected):
    name = str(path.relative_to(ROOT))
    before = path.stat()
    identity = {'sha256': sha(path), 'bytes': before.st_size}
    after = path.stat()
    assert (before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns), name
    if name in REPORTS or expected.get(name) != identity:
        entries.append({'path': name, **identity, 'mode': stat.S_IMODE(after.st_mode)})
assert str(SNAPSHOT.relative_to(ROOT)) in {entry['path'] for entry in entries}
assert str(cut_path.relative_to(ROOT)) in {entry['path'] for entry in entries}
with tarfile.open(ARCHIVE, 'w:gz') as tar:
    for entry in entries:
        path = ROOT / entry['path']
        assert sha(path) == entry['sha256']
        tar.add(path, arcname=entry['path'], recursive=False)
with tarfile.open(ARCHIVE) as tar:
    by_name = {entry['path']: entry for entry in entries}
    members = tar.getmembers()
    assert len(members) == len(entries)
    for member in members:
        assert member.isfile() and member.name in by_name
        raw = tar.extractfile(member).read()
        assert len(raw) == by_name[member.name]['bytes'] and hashlib.sha256(raw).hexdigest() == by_name[member.name]['sha256']

# Apply only to the newly generated isolated source restore, never the workspace.
for name, identity in expected.items(): assert sha(restore / name) == identity['sha256'], name
spec = importlib.util.spec_from_file_location('final_owned_overlay_extract', restore / 'agent/research/continuation-20261120/seal_recovery_delta_v7.py')
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)
for entry in entries:
    destination = restore / entry['path']
    assert not destination.is_symlink() and destination.resolve().is_relative_to(restore)
extractor.extract(ARCHIVE, restore)
effective = dict(expected)
effective.update({entry['path']: {'sha256': entry['sha256'], 'bytes': entry['bytes']} for entry in entries})
for name, identity in effective.items():
    path = restore / name
    assert path.is_file() and path.stat().st_size == identity['bytes'] and sha(path) == identity['sha256'], name
assert sha(ROOT / '.git/index') == baseline['index_sha256']
report_hashes = {name: sha(ROOT / name) for name in REPORTS}
for name in REPORTS: assert report_hashes[name] == sha(restore / name)
envelope = {'at': now().isoformat(), 'status': 'FINAL_ROOT_AND_LATE_METADATA_ENVELOPE_VERIFIED_ON_ISOLATED_RESTORE',
    'source_cut': {'receipt_path': str(cut_path.relative_to(ROOT)), 'receipt_sha256': sha(cut_path), 'delta_archive': cut['delta_archive']},
    'archive': {'path': str(ARCHIVE.relative_to(ROOT)), 'sha256': sha(ARCHIVE), 'bytes': ARCHIVE.stat().st_size},
    'entries': entries, 'effective_expected_file_count_after_overlay': len(effective),
    'all_effective_hashes_verified_after_actual_overlay': True, 'restored_root': str(restore),
    'root_report_hashes': report_hashes, 'final_inventory_snapshot': {'path': str(SNAPSHOT.relative_to(ROOT)), 'sha256': sha(SNAPSHOT)},
    'restored_candidate_index_consumption': {'path': str(consumption_path.relative_to(ROOT)), 'sha256': sha(consumption_path)},
    'self_and_outer_receipt_excluded_from_archive': True, 'source_current_delta_separate_not_recursively_embedded': True,
    'source_executed': False, 'model_calls': 0, 'optimizer_steps': 0, 'owner_gold': 0,
    'cold_boot_remote_durability_or_training_recovery_claimed': False}
fill_pending(ENVELOPE_RECEIPT, envelope)
ended = now()
closing = {'at': ended.isoformat(), 'local': ended.astimezone(ZoneInfo('America/Sao_Paulo')).isoformat(),
    'campaign_status': 'COMPLETED_MEASURED_MINIMUM_WITH_EXPLICIT_PRODUCT_LIMITATIONS',
    'actual_start_utc': baseline['start_utc'], 'actual_end_utc': ended.isoformat(),
    'elapsed_seconds': (ended - start).total_seconds(), 'minimum_target_utc': baseline['minimum_target_utc'],
    'eleven_hours_achieved': ended >= minimum,
    'closing_reason': 'Measured minimum met; authorized substantive research and final source/report/control preservation completed. No observed early termination condition used.',
    'head': head, 'index_sha256': baseline['index_sha256'], 'head_and_index_unchanged': True,
    'current_source_versions': {'caller': '1.9.43', 'helper': '0.1.5', 'planner': '0.3.6', 'maintenance': '0.1.5'},
    'operational_manifest_sha256': sha(source_index), 'source_cut': cut,
    'final_envelope_receipt': {'path': str(ENVELOPE_RECEIPT.relative_to(ROOT)), 'sha256': sha(ENVELOPE_RECEIPT)},
    'final_envelope_archive': envelope['archive'], 'all_effective_hashes_verified_after_actual_overlay': True,
    'effective_recovered_file_count': len(effective), 'root_report_hashes': report_hashes,
    'final_inventory_snapshot': envelope['final_inventory_snapshot'],
    'inventory_counts': {key: snapshot[key] for key in ['created_count', 'modified_count', 'deleted_count']},
    'all_three_late_control_paths_emitted_without_claiming_placeholder_identities': True,
    'model_calls_complete': 9, 'active_model_calls': 0, 'generated_tokens': 8140, 'server_seconds': 4085.0593952430004,
    'all_nine_complete_requested_outputs_rejected': True, 'frozen_dataset_records_unchanged': 305,
    'optimizer_steps': 0, 'owner_gold': 0, 'fine_tuning': 'NO-GO0/9FULLY_SATISFIED', 'publication': False,
    'existing_tests': {'agent_python': '312PASS', 'linux_existing_subset_not_additional': '68PASS', 'ruby': '262PASS/1787assertions', 'backend_python': '3PASS', 'frontend': '100/102;two unchanged input failures'},
    'already_loaded_Rails_caller_version_measured': False, 'service_restarted': False,
    'active_or_uncertain_operations': [], 'next_safe_action': 'Read four root reports,verify this receipt/source assets/envelope hashes,use current relative candidate index and queue;owner review before publication or any future training.',
    'limits': 'Measured campaign/source/evidence/root-report recovery only. No certified neural holdout,general semantic accuracy,automatic publication,training,full OS/cold boot or remote backup.',
    'self_sha256_not_embedded': True, 'outer_control_receipt_delivered_alongside_archives': True,
    'final_envelope_wall_seconds': time.monotonic() - started}
assert closing['eleven_hours_achieved'] is True
fill_pending(CLOSING, closing)
print(json.dumps({'status': closing['campaign_status'], 'actual_end_utc': closing['actual_end_utc'],
    'elapsed_seconds': closing['elapsed_seconds'], 'effective_recovered_files': len(effective),
    'inventory_counts': closing['inventory_counts'], 'envelope_members': len(entries),
    'envelope_sha256': envelope['archive']['sha256'], 'closing_receipt_sha256': sha(CLOSING),
    'head_and_index_unchanged': True, 'owner_gold': 0, 'optimizer_steps': 0}))
