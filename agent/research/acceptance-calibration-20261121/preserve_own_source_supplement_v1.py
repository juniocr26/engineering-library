"""Preserve selected unchanged own sources/tests, restore and import own modules only."""
from pathlib import Path
import datetime,hashlib,io,json,os,stat,subprocess,sys,tarfile,tempfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
ledger=json.loads((P/'own-selected-inspected-files-v1.json').read_text())
assert len(ledger['rows'])==13 and ledger['all_hashes_match_HEAD']
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_preservation':True,
 'source_ledger':'own-selected-inspected-files-v1.json','source_ledger_sha256':hashlib.sha256((P/'own-selected-inspected-files-v1.json').read_bytes()).hexdigest(),
 'files':[{'path':r['path'],'sha256':r['worktree_sha256'],'purpose':r['purpose']}for r in ledger['rows']],
 'scope':'Restricted13selectedunchangedownsource/testfiles. Restore/hash/mode/import6Pythonmodulesonly; no app/helper/test/native execution. Supplements420basecapsule,2overlappingmodulesmustmatch;431distinctselectedinputsifcolocated. Notalltransitiveapp/frontend/Ruby/native/Gohelperdependencies.'}
with(P/'own-source-recovery-supplement-protocol-v1.json').open('x')as stream:json.dump(protocol,stream,indent=2);stream.write('\n')
B=ROOT/'.local-backups/acceptance-calibration-20261121/own-source-recovery-supplement-v1';B.mkdir(mode=0o700)
archive=B/'restricted-own-source-inputs.tar.gz';entries=[]
with tarfile.open(archive,'w:gz')as tar:
 for row in protocol['files']:
  path=ROOT/row['path'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256']
  mode=stat.S_IMODE(path.stat().st_mode);info=tarfile.TarInfo(row['path']);info.size=len(raw);info.mode=mode
  tar.addfile(info,io.BytesIO(raw));entries.append({**row,'mode':mode,'bytes':len(raw)})
os.chmod(archive,0o600)
manifest=B/'input-manifest.json';manifest.write_text(json.dumps({'classification':'RESTRICTED_OWN_PROPRIETARY_SOURCE_AND_EXISTING_TESTS_NOT_PUBLIC_TRAINING','files':entries},indent=2)+'\n');os.chmod(manifest,0o600)
restored=Path(tempfile.mkdtemp(prefix='el-own-source-supplement-',dir='/private/tmp'))
with tarfile.open(archive)as tar:
 members=tar.getmembers();assert len(members)==13
 for member,row in zip(members,entries,strict=True):
  relative=Path(member.name);assert member.isfile()and member.name==row['path']and not relative.is_absolute()and'..'not in relative.parts
  dest=restored/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(tar.extractfile(member).read());os.chmod(dest,row['mode'])
  assert hashlib.sha256(dest.read_bytes()).hexdigest()==row['sha256']and stat.S_IMODE(dest.stat().st_mode)==row['mode']
code="""import json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'agent/tools'))
import documentation_workspace as w, documentation_job_budget as j, documentation_lifecycle as l, documentation_candidates as c, documentation_retrieval as r, documentation_maintenance as m
mods=[w,j,l,c,r,m]
assert all(Path(mod.__file__).is_relative_to(Path.cwd())for mod in mods)
print(json.dumps({'module_paths':[mod.__file__for mod in mods],'versions':{mod.__name__:getattr(mod,'VERSION',None)for mod in mods},'helper_dispatched':False,'test_suites_run':False}))
"""
command=[sys.executable,'-B','-c',code];out=subprocess.run(command,cwd=restored,capture_output=True,timeout=20)
with(B/'restore-import.stdout').open('xb')as stream:stream.write(out.stdout)
with(B/'restore-import.stderr').open('xb')as stream:stream.write(out.stderr)
assert out.returncode==0,out.stderr.decode()
observed=json.loads(out.stdout)
assert observed['versions']['documentation_lifecycle']=='0.3.6'and observed['versions']['documentation_retrieval']=='0.1.5'and observed['versions']['documentation_maintenance']=='0.1.5'
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':str(archive.relative_to(ROOT)),
 'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'manifest':str(manifest.relative_to(ROOT)),
 'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'restored_root':str(restored),
 'files_restored_and_hash_mode_verified':13,'own_modules_imported':6,'import_command':command,'import_observation':observed,
 'base_capsule_overlap':2,'new_distinct_selected_inputs':11,'combined_distinct_selected_inputs':431,
 'classification':'RESTRICTED_INTERNAL_LOCAL_ONLY; source/testsnapshotsnotnewpermanenttestsortrainingexamples',
 'not_full_transitive_cleanclone_or_native_recovery':True,'production_changes':0,'test_reruns':0,'model_calls':0,'gold':0,'optimizer_updates':0}
with(P/'own-source-recovery-supplement-v1.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
(B/'receipt-redundant-copy.json').write_bytes((P/'own-source-recovery-supplement-v1.json').read_bytes());os.chmod(B/'receipt-redundant-copy.json',0o600)
print(json.dumps({k:v for k,v in receipt.items()if k not in ['import_command','import_observation']},indent=2))
