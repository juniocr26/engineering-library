"""Create immutable local research checkpoints and actually restore/replay them."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import stat
import subprocess
import tarfile
import tempfile

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--number', required=True, type=int)
args = parser.parse_args()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
reports = [ROOT/name for name in ['AI_TRAINING_CAMPAIGN_REPORT.md', 'AI_TRAINING_FILE_INVENTORY.md', 'AI_FINE_TUNING_READINESS.md', 'AI_TRAINING_RESUME.md']]
sources = [x for x in P.rglob('*') if x.is_file() and not x.is_symlink() and '__pycache__' not in x.parts]
# Preserve the actual dependency closure of the finite binding profile, not just its manifest.
anchor = json.loads((P/'trusted-binding-anchor-v1.json').read_text())
sources += [ROOT/edge['path'] for bundle in anchor.values() for edge in bundle['dependencies']]
sources += reports
helper_protocol = json.loads((P/'helper-admission-protocol-v1.json').read_text())
sources += [ROOT/item['path'] for item in helper_protocol['dependencies']]
sources = sorted(set(sources))
folder = ROOT/'.local-backups/final-intensive-20261121'/f'checkpoint-{args.number:03d}'
folder.mkdir(parents=True, mode=0o700, exist_ok=False)
os.chmod(folder, 0o700)
manifest = []
for path in sources:
    assert not path.is_symlink()
    manifest.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size,
                     'mode': stat.S_IMODE(path.stat().st_mode)})
archive = folder/'research-reports-and-selected-dependencies.tar.gz'
with tarfile.open(archive, 'x:gz') as tar:
    for entry in manifest:
        tar.add(ROOT/entry['path'], arcname=entry['path'], recursive=False)
os.chmod(archive, 0o600)
with (folder/'input-manifest.json').open('x') as stream:
    json.dump(manifest, stream, indent=2)
    stream.write('\n')
os.chmod(folder/'input-manifest.json', 0o600)
restored = Path(tempfile.mkdtemp(prefix=f'el-final-{args.number:03d}-', dir='/private/tmp'))
with tarfile.open(archive) as tar:
    # All members originate from the exact trusted regular-file list above.
    assert all(member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts for member in tar.getmembers())
    tar.extractall(restored, filter='data')
for entry in manifest:
    target = restored/entry['path']
    assert sha(target.read_bytes()) == entry['sha256']
    assert stat.S_IMODE(target.stat().st_mode) == entry['mode']
relative_research = P.relative_to(ROOT)
command = [os.sys.executable, '-B', '-c',
           'from pathlib import Path;import json,sys; p=Path(sys.argv[1]);sys.path.insert(0,str(p));import binding_envelope_v1 as v; a=json.loads((p/"trusted-binding-anchor-v1.json").read_text());root=p.parents[2];out={k:v.validate(v.canonical(x),x,root) for k,x in a.items()};print(json.dumps(out));assert all(not r for r in out.values())',
           str(restored/relative_research)]
replay = subprocess.run(command, capture_output=True, text=True, timeout=30, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
ast_command = [os.sys.executable, '-B', '-c',
               'from pathlib import Path;import json,sys; p=Path(sys.argv[1]);sys.path.insert(0,str(p));import observe_exception_scope_v2 as v; protocol=json.loads((p/"exception-scope-protocol-v2.json").read_text());rows=[v.flags((p/c["helper"]).read_text(),(p/c["job"]).read_text())[0]==c["expected"] for c in protocol["cases"]];print(json.dumps({"matched":sum(rows),"cases":len(rows)}));assert all(rows)',
               str(restored/relative_research)]
ast_replay = subprocess.run(ast_command, capture_output=True, text=True, timeout=30, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
assert ast_replay.returncode == 0, ast_replay.stderr
helper_command = [os.sys.executable, '-B', '-c',
                  'from pathlib import Path;import json,sys; p=Path(sys.argv[1]);root=p.parents[2];sys.path.insert(0,str(root/"agent/tools"));import documentation_retrieval as h; protocol=json.loads((p/"helper-admission-protocol-v1.json").read_text());observations=[]\nfor c in protocol["tasks"]:\n raw=(p/"reacquired-public-sources"/c["task"]/c["path"]).read_bytes()\n try:\n  unit=h.extract(raw.decode(),c["selector"],c["language"]);h.validate_unit(unit,raw,c["selector"],c["language"]);status="ADMITTED_LEXICAL_UNIT"\n except Exception as error: status="REFUSED"\n observations.append(status==c["expected"])\nprint(json.dumps({"matched":sum(observations),"cases":len(observations)}));assert all(observations)',
                  str(restored/relative_research)]
helper_replay = subprocess.run(helper_command, capture_output=True, text=True, timeout=60, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
assert helper_replay.returncode == 0, helper_replay.stderr
result = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checkpoint': args.number,
          'archive': str(archive.relative_to(ROOT)), 'archive_sha256': sha(archive.read_bytes()), 'archive_bytes': archive.stat().st_size,
          'input_manifest': str((folder/'input-manifest.json').relative_to(ROOT)), 'input_manifest_sha256': sha((folder/'input-manifest.json').read_bytes()),
          'regular_files_restored_and_hash_verified': len(manifest), 'file_modes_verified': True,
          'restored_root': str(restored), 'consumer_replay': {'command': command, 'exit_code': replay.returncode, 'stdout': replay.stdout, 'stderr': replay.stderr},
          'exception_scope_consumer_replay': {'command': ast_command, 'exit_code': ast_replay.returncode, 'stdout': ast_replay.stdout, 'stderr': ast_replay.stderr},
          'helper_admission_consumer_replay': {'command': helper_command, 'exit_code': helper_replay.returncode, 'stdout': helper_replay.stdout, 'stderr': helper_replay.stderr},
          'scope': 'Local checkpoint and finite receipt-integrity consumer replay only. Not clean clone, model/optimizer, remote backup, Windows, crash durability or semantic correctness.',
          'self_cut': 'This receipt and manifest are outside own archive; later checkpoint can include earlier receipt. No infinite self-hash closure.',
          'active_campaign': True, 'neural_calls': 0, 'optimizer_updates': 0, 'gold': 0}
assert replay.returncode == 0, replay.stderr
name = f'checkpoint-{args.number:03d}.json'
for destination in [P/name, folder/'receipt.json']:
    with destination.open('x') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
print(json.dumps({key: result[key] for key in ['checkpoint', 'regular_files_restored_and_hash_verified', 'archive_bytes', 'consumer_replay', 'exception_scope_consumer_replay', 'helper_admission_consumer_replay']}))
