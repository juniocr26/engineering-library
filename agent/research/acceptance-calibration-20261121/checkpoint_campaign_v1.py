"""Preserve a point-in-time research cut and actually restore every member."""
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--checkpoint', required=True, type=int)
args = parser.parse_args()
if args.checkpoint < 2:
    raise SystemExit('Checkpoint001 already preserved by original command')
backup = ROOT / '.local-backups/acceptance-calibration-20261121' / ('checkpoint-%03d' % args.checkpoint)
backup.mkdir(parents=True, exist_ok=False)
reports = [ROOT / name for name in ['AI_TRAINING_CAMPAIGN_REPORT.md', 'AI_TRAINING_FILE_INVENTORY.md',
                                  'AI_FINE_TUNING_READINESS.md', 'AI_TRAINING_RESUME.md']]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


pending = []
selected = []
for path in sorted(HERE.rglob('*')):
    if path.is_symlink():
        selected.append(path)
        continue
    if not path.is_file():
        continue
    if 'generation-v1' in path.parts and (path.parent / 'started.json').exists():
        terminal = False
        try:
            terminal = 'ended_at' in json.loads((path.parent / 'outcome.json').read_text())
        except (ValueError, OSError):
            pass
        if not terminal and path.name not in ['request.json', 'started.json', 'process.json']:
            pending.append(str(path.relative_to(ROOT)))
            continue
        if path.name in ['started.json', 'process.json']:
            try:
                json.loads(path.read_text())
            except (ValueError, OSError):
                pending.append(str(path.relative_to(ROOT)))
                continue
    selected.append(path)
selected.extend(reports)
restored = Path(tempfile.mkdtemp(prefix='el-acceptance-%03d-' % args.checkpoint, dir='/private/tmp'))


def archive_and_restore(paths, archive):
    entries = []
    with tarfile.open(archive, 'w:gz') as tar:
        for path in paths:
            relative = path.relative_to(ROOT).as_posix()
            info = tarfile.TarInfo(relative)
            info.mode = 0o600
            if path.is_symlink():
                target = os.readlink(path)
                if Path(target).is_absolute() or '..' in Path(target).parts:
                    raise ValueError('Unsafe symlink target refused, never followed')
                info.type = tarfile.SYMTYPE
                info.linkname = target
                tar.addfile(info)
                entries.append({'path': relative, 'kind': 'symlink', 'target': target,
                                'target_text_sha256': sha(target.encode())})
            else:
                raw = path.read_bytes()
                info.size = len(raw)
                tar.addfile(info, io.BytesIO(raw))
                entries.append({'path': relative, 'kind': 'file', 'bytes': len(raw), 'sha256': sha(raw)})
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        if len(members) != len(entries):
            raise ValueError('Archive member count differs')
        for member, entry in zip(members, entries, strict=True):
            relative = Path(member.name)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe archive member refused')
            destination = restored / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if entry['kind'] == 'symlink':
                if not member.issym() or member.linkname != entry['target']:
                    raise ValueError('Symlink archive mismatch')
                destination.symlink_to(entry['target'])
                if not destination.is_symlink() or sha(os.readlink(destination).encode()) != entry['target_text_sha256']:
                    raise ValueError('Restored symlink differs')
            else:
                if not member.isfile():
                    raise ValueError('Nonfile archive member refused')
                raw = tar.extractfile(member).read()
                destination.write_bytes(raw)
                if file_sha(destination) != entry['sha256']:
                    raise ValueError('Restored file checksum differs')
    return entries


common_archive = backup / 'research-and-root-reports.tar.gz'
entries = archive_and_restore(selected, common_archive)
log_root = ROOT / '.local-backups/acceptance-calibration-20261121'
logs = [path for path in sorted(log_root.rglob('*.log'))
        if not any(part.startswith('checkpoint-') for part in path.relative_to(log_root).parts)]
log_archive = backup / 'restricted-runtime-and-test-logs.tar.gz'
log_entries = archive_and_restore(logs, log_archive)
manifest_path = backup / 'input-manifest.json'
manifest_path.write_text(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                   'classification': 'RESTRICTED_INTERNAL_LOCAL_ONLY; proprietaryELsourcequotes in proposal, not training/publication',
                                   'files': entries, 'separate_logs': log_entries,
                                   'open_worker_files_excluded': pending}, indent=2) + '\n')
git = subprocess.run(['/opt/homebrew/bin/git', '--no-optional-locks', 'status', '--porcelain=v1'],
                     cwd=ROOT, capture_output=True, text=True, check=True)
receipt = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'status': 'ACTIVE_POINT_IN_TIME_CHECKPOINT_RESTORED_AND_VERIFIED',
           'archive': str(common_archive.relative_to(ROOT)), 'archive_sha256': file_sha(common_archive),
           'manifest': str(manifest_path.relative_to(ROOT)), 'manifest_sha256': file_sha(manifest_path),
           'common_file_members_restored_and_verified': sum(e['kind'] == 'file' for e in entries),
           'common_symlink_members_restored_and_verified_without_following': sum(e['kind'] == 'symlink' for e in entries),
           'restricted_logs_archive': str(log_archive.relative_to(ROOT)),
           'restricted_logs_archive_sha256': file_sha(log_archive), 'log_files_restored_and_verified': len(log_entries),
           'restored_root': str(restored), 'open_worker_files_excluded': pending,
           'git_status': git.stdout, 'git_index_sha256': file_sha(ROOT / '.git/index'),
           'no_weights_copied': True, 'not_clean_clone_coldboot_or_remote_restore': True,
           'not_campaign_complete': True, 'owner_gold': 0, 'optimizer_updates': 0,
           'self_cut': 'This receipt and input manifest are outside their own archives; redundant receipt copy preserved. Next checkpoint includes earlier receipts.'}
receipt_path = HERE / ('recovery-checkpoint-%03d.json' % args.checkpoint)
with receipt_path.open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
(backup / 'receipt-redundant-copy.json').write_bytes(receipt_path.read_bytes())
print(json.dumps(receipt, indent=2), flush=True)
