"""Seal current technical evidence as a delta over the verified intermediate cut."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import stat
import shutil
import subprocess
import sys
import tarfile
import time

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
OUT = ROOT / '.local-backups/continuation-20261120/recovery-delta-v5'
RESTORE = Path('/private/tmp/el-engineering-library-continuation-20261120-cut-v5-restore')


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def extract(archive, root, skip=()):
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            name = Path(member.name)
            if name.is_absolute() or '..' in name.parts or not (member.isfile() or member.isdir()):
                raise ValueError('unsafe archive member: ' + member.name)
            if member.name in skip:
                continue
            target = root / name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as source, target.open('wb') as dest:
                while block := source.read(1024 * 1024):
                    dest.write(block)
            target.chmod(member.mode & 0o777)


def main():
    start = time.monotonic()
    OUT.mkdir(exist_ok=False)
    baseline = json.loads((P / 'baseline.json').read_text())
    parent_receipt = json.loads((P / 'recovery-delta-receipt-v4.json').read_text())
    parent_manifest_path = ROOT / parent_receipt['input_manifest']['path']
    assert sha(parent_manifest_path) == parent_receipt['input_manifest']['sha256']
    parent = json.loads(parent_manifest_path.read_text())
    assets = parent_receipt['parent_assets']
    for asset in assets:
        assert sha(ROOT / asset['path']) == asset['sha256']
    effective_parent = {**parent_receipt['delta_archive'], 'role': 'effective_parent_delta_v4'}
    assert sha(ROOT / effective_parent['path']) == effective_parent['sha256']
    assets = assets + [effective_parent]
    skip = set(parent['skip_live_baseline_paths'])
    expected = dict(parent['effective_expected_files'])
    expected[effective_parent['path']] = {'sha256': effective_parent['sha256'], 'bytes': effective_parent['bytes']}
    active_pending_paths = {str((P/'backoff-model-chapter-v1'/name).relative_to(ROOT)) for name in ['response.json','outcome.json','error.json','review.json']}
    selected = set()
    selected.update(ROOT / name for name in ['backend/lib/documentation/command.rb', 'backend/lib/documentation/python_structure.py', 'agent/tools/documentation_retrieval.py', 'agent/recovery/manifest.json', 'AI_TRAINING_CAMPAIGN_REPORT.md', 'AI_TRAINING_FILE_INVENTORY.md', 'AI_FINE_TUNING_READINESS.md', 'AI_TRAINING_RESUME.md'])
    for path in P.rglob('*'):
        if path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts and str(path.relative_to(ROOT)) not in active_pending_paths:
            selected.add(path)
    parent_cut = ROOT / '.local-backups/continuation-20261120/intermediate-cut-v1'
    for path in (ROOT / '.local-backups/continuation-20261120').rglob('*'):
        if not path.is_file() or path.is_symlink() or path.is_relative_to(OUT):
            continue
        if path.is_relative_to(parent_cut) and path.suffix == '.gz':
            continue  # Parent archives remain independent chain assets, never recursively embedded.
        selected.add(path)
    delta_entries = []
    observed_selected = []
    for path in sorted(selected):
        assert stat.S_ISREG(path.lstat().st_mode)
        name = str(path.relative_to(ROOT))
        before = path.stat()
        identity = {'sha256': sha(path), 'bytes': before.st_size}
        after = path.stat()
        assert (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns), 'input changed while hashing: '+name
        observed_selected.append({'path': name, **identity})
        if expected.get(name) != identity:
            delta_entries.append({'path': name, **identity, 'mode': stat.S_IMODE(path.stat().st_mode)})
        expected[name] = identity
    authorized_modified = {'backend/lib/documentation/command.rb', 'backend/lib/documentation/python_structure.py', 'agent/tools/documentation_retrieval.py', 'agent/recovery/manifest.json'}
    for name, identity in baseline['tracked_identity'].items():
        path = ROOT / name
        if name in skip:
            assert not path.exists()
        elif name not in authorized_modified:
            assert path.is_file() and sha(path) == identity['sha256'], 'unexpected tracked drift: ' + name
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, env=env, text=True).strip()
    assert head == baseline['head'] and sha(ROOT / '.git/index') == baseline['index_sha256']
    manifest = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'parent_assets': assets, 'parent_manifest': {'path': str(parent_manifest_path.relative_to(ROOT)), 'sha256': sha(parent_manifest_path)}, 'delta_entries': delta_entries, 'effective_expected_files': expected, 'current_selected_files': observed_selected, 'skip_live_baseline_paths': sorted(skip), 'production_modified_files': sorted(authorized_modified), 'excluded': ['transient __pycache__ bytecode', 'self-referential current recovery-delta-v5 output archive/receipt', 'recursively embedded parent archive bytes'], 'active_pending_output_paths_excluded': sorted(active_pending_paths), 'effective_parent_cut': 'V4', 'model_store_and_bundle_separate': True, 'model_weights_copied': False, 'full_cold_runtime_or_remote_durability_claim': False}
    save(OUT / 'input-manifest.json', manifest)
    archive = OUT / 'current-delta.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        for entry in delta_entries:
            path = ROOT / entry['path']
            assert sha(path) == entry['sha256'], 'input changed during sealing'
            tar.add(path, arcname=entry['path'], recursive=False)
    RESTORE.mkdir(exist_ok=False)
    extract(ROOT / assets[0]['path'], RESTORE, skip)
    extract(ROOT / assets[1]['path'], RESTORE)
    extract(ROOT / effective_parent['path'], RESTORE)
    extract(archive, RESTORE)
    for asset in assets[2:]:
        source = ROOT / asset['path']; target = RESTORE / asset['path']
        assert sha(source) == asset['sha256']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for name, identity in expected.items():
        path = RESTORE / name
        assert path.is_file() and path.stat().st_size == identity['bytes'] and sha(path) == identity['sha256'], 'restored identity mismatch: ' + name
    bootstrap = subprocess.run([sys.executable, str(RESTORE / 'agent/recovery/bootstrap.py'), 'knowledge'], cwd=RESTORE, env=env, text=True, capture_output=True, timeout=90)
    (OUT / 'restored-bootstrap.stdout').write_text(bootstrap.stdout)
    (OUT / 'restored-bootstrap.stderr').write_text(bootstrap.stderr)
    assert bootstrap.returncode == 0, bootstrap.stderr
    bootstrap_result = json.loads(bootstrap.stdout)
    # Input set identities stay true even if bootstrap materializes its six embedded small blobs.
    for name, identity in expected.items():
        assert sha(RESTORE / name) == identity['sha256'], 'bootstrap altered a restored expected input: ' + name
    result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'VERIFIED_INCREMENTAL_SOURCE_AND_TECHNICAL_EVIDENCE_DELTA_OVER_V4', 'wall_seconds': time.monotonic() - start, 'delta_archive': {'path': str(archive.relative_to(ROOT)), 'sha256': sha(archive), 'bytes': archive.stat().st_size}, 'input_manifest': {'path': str((OUT / 'input-manifest.json').relative_to(ROOT)), 'sha256': sha(OUT / 'input-manifest.json')}, 'parent_assets': assets, 'delta_file_count': len(delta_entries), 'effective_expected_file_count': len(expected), 'all_expected_file_hashes_verified_before_and_after_bootstrap': True, 'restored_root': str(RESTORE), 'restored_bootstrap': bootstrap_result, 'head_unchanged': head == baseline['head'], 'index_unchanged': sha(ROOT / '.git/index') == baseline['index_sha256'], 'effective_parent_cut': 'V4', 'active_pending_output_paths_excluded': sorted(active_pending_paths), 'source_native_experiments_rerun': False, 'neural_inference_or_training_rerun': False, 'model_weights_copied': False, 'remote_durability_or_cold_boot_verified': False, 'eleven_hours_claimed': False, 'point_in_time_scope': 'Later root-report updates/new receipts are not claimed inside this cut; chain assets and model store remain separately preserved.'}
    save(OUT / 'receipt.json', result)
    save(P / 'recovery-delta-receipt-v5.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ['parent_assets', 'point_in_time_scope']}), flush=True)


if __name__ == '__main__':
    main()
