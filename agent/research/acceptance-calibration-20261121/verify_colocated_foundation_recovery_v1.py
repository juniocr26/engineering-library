"""Restore opaque original direct inputs into a new checkpoint's private root."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import stat
import subprocess
import sys
import tarfile

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--checkpoint', required=True, type=int)
args = parser.parse_args()
checkpoint_file = P / ('recovery-checkpoint-%03d.json' % args.checkpoint)
checkpoint = json.loads(checkpoint_file.read_text())
root = Path(checkpoint['restored_root']).resolve()
assert root.is_relative_to(Path('/private/tmp')) and root.name.startswith('el-acceptance-')
foundation = json.loads((P / 'foundation-input-capsule-recovery-v1.json').read_text())
archive = root / foundation['archive']
manifest = root / foundation['manifest']
sha = lambda raw: hashlib.sha256(raw).hexdigest()
assert sha(archive.read_bytes()) == foundation['archive_sha256']
assert sha(manifest.read_bytes()) == foundation['manifest_sha256']
entries = json.loads(manifest.read_text())['files']

with tarfile.open(archive) as tar:
    members = tar.getmembers()
    assert len(members) == len(entries) == 420
    for member, entry in zip(members, entries, strict=True):
        relative = Path(member.name)
        assert member.isfile() and member.name == entry['path']
        assert not relative.is_absolute() and '..' not in relative.parts
        target = root / relative
        # Never repair or overwrite an earlier restoration in place.
        assert not target.exists() and not target.is_symlink()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(tar.extractfile(member).read())
        os.chmod(target, entry['mode'])
        assert sha(target.read_bytes()) == entry['sha256']
        assert stat.S_IMODE(target.stat().st_mode) == entry['mode']

code = '''import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'agent/tools'))
import documentation_job_budget as jobs
import documentation_workspace as workspace
print(json.dumps({'job_version':jobs.VERSION,'implementation_sha256':jobs.IMPLEMENTATION_SHA256,'workspace_sha256':jobs.WORKSPACE_SHA256,'job_module':jobs.__file__,'workspace_module':workspace.__file__,'POSIX_lock_module_available':jobs.fcntl is not None,'helper_dispatched':False}))
'''
command = [sys.executable, '-B', '-c', code]
observed = subprocess.run(command, cwd=root, capture_output=True, timeout=20)
assert observed.returncode == 0, observed.stderr.decode()
imports = json.loads(observed.stdout)
expected = {entry['path']: entry['sha256'] for entry in entries}
assert imports['implementation_sha256'] == expected['agent/tools/documentation_job_budget.py']
assert imports['workspace_sha256'] == expected['agent/tools/documentation_workspace.py']
assert Path(imports['job_module']).is_relative_to(root)
assert Path(imports['workspace_module']).is_relative_to(root)
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'checkpoint': args.checkpoint,
          'checkpoint_receipt_sha256': sha(checkpoint_file.read_bytes()),
          'restored_root': str(root), 'opaque_direct_inputs_restored_and_hash_mode_verified': 420,
          'foundation_archive_from_restored_supporting_evidence': str(archive),
          'foundation_archive_sha256': foundation['archive_sha256'],
          'selected_own_module_import_command': command,
          'selected_own_module_import_observation': imports,
          'private_eval_body_semantic_decoding': False,
          'runtime_scope': 'Current research plus original7datasets/398directreferences/15selectedinputs co-located and two restored own modules imported. Common checkpoint separately replays restored owned Go AST observer. Not all transitive research dependencies, apps, model, native framework, clean clone/cold boot or neural adapter restore.',
          'helper_or_upstream_program_execution': False,
          'production_files_modified': 0, 'gold': 0, 'optimizer_updates': 0}
receipt_path = P / ('foundation-colocated-recovery-checkpoint-%03d-v1.json' % args.checkpoint)
with receipt_path.open('x') as stream:
    json.dump(result, stream, indent=2); stream.write('\n')
backup = ROOT / '.local-backups/acceptance-calibration-20261121' / ('checkpoint-%03d' % args.checkpoint)
(backup / 'foundation-colocated-recovery-receipt.json').write_bytes(receipt_path.read_bytes())
print(json.dumps(result, indent=2))
