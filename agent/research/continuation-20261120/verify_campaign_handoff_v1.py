"""Read-only final handoff verifier; no extraction, Git writes or inspected-source execution."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile

P = Path(__file__).resolve().parent
ROOT = P.parents[2]

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def local(name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Non-relative handoff path')
    selected = ROOT / path
    if selected.is_symlink() or not selected.resolve().is_relative_to(ROOT):
        raise ValueError('Handoff path escapes current root')
    return selected

def identity(asset):
    file = local(asset['path'])
    if not file.is_file() or sha(file) != asset['sha256']:
        raise ValueError('Asset hash mismatch: ' + asset['path'])
    if 'bytes' in asset and file.stat().st_size != asset['bytes']:
        raise ValueError('Asset byte count mismatch: ' + asset['path'])
    return file

def require(condition, message):
    if not condition:
        raise ValueError(message)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--expected-closing-sha256', required=True, help='Use the SHA256 supplied with the completed campaign, not a value read from the same receipt.')
parser.add_argument('--verify-restored-root', action='store_true', help='Additionally hash the already-created isolated restore named by the receipt; does not extract or execute it.')
args = parser.parse_args()
require(len(args.expected_closing_sha256) == 64 and all(c in '0123456789abcdef' for c in args.expected_closing_sha256), 'Invalid expected receipt SHA256')
closing_path = P / 'closing-receipt-v1.json'
require(sha(closing_path) == args.expected_closing_sha256, 'Outer closing receipt hash differs')
closing = json.loads(closing_path.read_text())
baseline = json.loads((P / 'baseline.json').read_text())
start = datetime.datetime.fromisoformat(closing['actual_start_utc'])
end = datetime.datetime.fromisoformat(closing['actual_end_utc'])
minimum = datetime.datetime.fromisoformat(baseline['minimum_target_utc'])
require(closing['actual_start_utc'] == baseline['start_utc'], 'Start differs from baseline')
require(minimum - start == datetime.timedelta(hours=11), 'Minimum interval differs')
require(closing['eleven_hours_achieved'] is True and end >= minimum, 'Measured minimum not met')
require(abs((end - start).total_seconds() - closing['elapsed_seconds']) < 0.001, 'Elapsed interval differs')
require(closing['optimizer_steps'] == 0 and closing['owner_gold'] == 0 and closing['publication'] is False, 'Authority or no-training boundary differs')
envelope_path = identity(closing['final_envelope_receipt'])
envelope = json.loads(envelope_path.read_text())
archive = identity(closing['final_envelope_archive'])
require(envelope['archive'] == closing['final_envelope_archive'], 'Envelope archive identities disagree')
for name, digest in closing['root_report_hashes'].items():
    require(sha(local(name)) == digest, 'Current root report differs: ' + name)
require(closing['root_report_hashes'] == envelope['root_report_hashes'], 'Root report sets differ')
require(sha(ROOT / 'agent/recovery/manifest.json') == closing['operational_manifest_sha256'], 'Operational manifest differs')
identity(closing['final_inventory_snapshot'])
identity(envelope['restored_candidate_index_consumption'])
cut_reference = envelope['source_cut']
cut_path = identity({'path': cut_reference['receipt_path'], 'sha256': cut_reference['receipt_sha256']})
cut = json.loads(cut_path.read_text())
require(cut == closing['source_cut'], 'Source cut receipts differ')
identity(cut['delta_archive'])
input_manifest_path = identity(cut['input_manifest'])
inputs = json.loads(input_manifest_path.read_text())
for asset in cut['parent_assets']:
    identity(asset)
entries = envelope['entries']
by_name = {row['path']: row for row in entries}
require(len(by_name) == len(entries), 'Duplicate envelope member identity')
with tarfile.open(archive) as tar:
    seen = set()
    for member in tar:
        require(member.isfile() and member.name in by_name and member.name not in seen, 'Unexpected envelope member')
        local(member.name)
        row = by_name[member.name]
        digest = hashlib.sha256()
        size = 0
        with tar.extractfile(member) as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block); size += len(block)
        require(size == row['bytes'] and digest.hexdigest() == row['sha256'], 'Envelope member content differs: ' + member.name)
        seen.add(member.name)
require(seen == set(by_name), 'Envelope member missing')
restored_files = None
if args.verify_restored_root:
    restore = Path(envelope['restored_root']).resolve()
    require(restore.parent == Path('/private/tmp') and restore.name == 'el-engineering-library-continuation-20261120-cut-v7-restore', 'Unexpected restore root')
    expected = dict(inputs['effective_expected_files'])
    expected.update({row['path']: {'sha256': row['sha256'], 'bytes': row['bytes']} for row in entries})
    for name, row in expected.items():
        rel = Path(name)
        require(not rel.is_absolute() and '..' not in rel.parts, 'Unsafe restored member path')
        file = restore / rel
        require(not file.is_symlink() and file.resolve().is_relative_to(restore), 'Restored member escapes')
        require(file.is_file() and file.stat().st_size == row['bytes'] and sha(file) == row['sha256'], 'Restored member differs: ' + name)
    restored_files = len(expected)
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, env=env, text=True).strip()
require(head == baseline['head'] == closing['head'], 'HEAD differs')
require(sha(ROOT / '.git/index') == baseline['index_sha256'] == closing['index_sha256'], 'Index differs')
print(json.dumps({'status': 'READ_ONLY_FINAL_HANDOFF_IDENTITIES_VERIFIED', 'closing_sha256': args.expected_closing_sha256, 'elapsed_seconds': closing['elapsed_seconds'], 'parent_assets': len(cut['parent_assets']), 'envelope_members': len(entries), 'restored_files_verified': restored_files, 'head_and_index_unchanged': True, 'source_executed': False, 'extraction_performed': False, 'model_or_optimizer_executed': False, 'scope': 'Local identity verification only; external trust anchor, cold boot, remote durability and training recovery are not established by hashes alone.'}))
