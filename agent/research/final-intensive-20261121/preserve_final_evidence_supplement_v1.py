"""Preserve the finite post-CP054 evidence cut and actually restore its bytes."""
from pathlib import Path
import json,hashlib,datetime,tarfile,tempfile,stat,os
P=Path(__file__).resolve().parent;ROOT=P.parents[2];folder=ROOT/'.local-backups/final-intensive-20261121/checkpoint-054';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
proof=json.loads((P/'weekend-capsule-consumption-results-v5-final.json').read_bytes());assert proof['status']=='PASS_EXISTING_CAPSULE_STANDALONE_RECOVERY' and proof['exact_final_tail_reports_reconstructed']==4
original={e['path']:e for e in json.loads((folder/'input-manifest.json').read_bytes())};selected=[]
for f in P.rglob('*'):
 if not f.is_file() or f.is_symlink() or '__pycache__' in f.parts:continue
 name=str(f.relative_to(ROOT));e=original.get(name)
 if e is None or sha(f)!=e['sha256'] or f.stat().st_size!=e['bytes'] or stat.S_IMODE(f.stat().st_mode)!=e['mode']:selected.append(f)
reports=['AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md','AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md'];selected += [ROOT/n for n in reports]
selected += [folder/n for n in ['receipt.json','input-manifest.json','final-report-reconstruction-receipt-v1.json','bootstrap-weekend-consumer-v5.py','final-canonical-tail-v1.json']]
selected=sorted(set(selected));entries=[{'path':str(f.relative_to(ROOT)),'bytes':f.stat().st_size,'sha256':sha(f),'mode':stat.S_IMODE(f.stat().st_mode)} for f in selected]
archive=folder/'final-evidence-supplement-v1.tar.gz';manifest=folder/'final-evidence-supplement-input-manifest-v1.json'
with tarfile.open(archive,'x:gz') as tar:
 for e in entries:tar.add(ROOT/e['path'],arcname=e['path'],recursive=False)
os.chmod(archive,0o600)
with manifest.open('x') as f:json.dump(entries,f,indent=2);f.write('\n')
os.chmod(manifest,0o600)
restored=Path(tempfile.mkdtemp(prefix='el-final-closeout-evidence-',dir='/private/tmp'));os.chmod(restored,0o700)
with tarfile.open(archive,'r:gz') as tar:
 members=tar.getmembers();assert len(members)==len(entries) and len({m.name for m in members})==len(entries)
 assert all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in members)
 tar.extractall(restored,filter='data')
for e in entries:
 f=restored/e['path'];assert f.stat().st_size==e['bytes'] and sha(f)==e['sha256'] and stat.S_IMODE(f.stat().st_mode)==e['mode']
finalroot=Path(proof['restored_root'])
for n in reports:assert (restored/n).read_bytes()==(ROOT/n).read_bytes()==(finalroot/n).read_bytes()
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_FINITE_LATE_EVIDENCE_RESTORE','archive':str(archive.relative_to(ROOT)),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'input_manifest':str(manifest.relative_to(ROOT)),'input_manifest_sha256':sha(manifest),'restored_root':str(restored),'regular_files_restored_and_hash_verified':len(entries),'modes_verified':True,'four_current_report_bytes_match_workspace_and_final_bootstrap':True,'source_checkpoint':54,'scope':'Late selected research evidence, four final reports and five capsule metadata/code/tail sidecars. Core TAR is separate. Receipt itself, final acceptance accounting and handoff manifest are deliberately outside this archive. Not a remote/full-host/runtime/model-state backup. Bootstrap does not auto-extract supplement.','model_calls':0,'optimizer_updates':0}
for f in [P/'final-evidence-supplement-receipt-v1.json',folder/'final-evidence-supplement-receipt-v1.json']:
 with f.open('x') as s:json.dump(out,s,indent=2);s.write('\n')
 os.chmod(f,0o600)
print(json.dumps(out))
