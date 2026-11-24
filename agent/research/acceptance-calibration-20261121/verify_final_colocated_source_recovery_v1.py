"""Add selected own source supplement to the already restored420foundationinputs."""
from pathlib import Path
import datetime,hashlib,json,os,stat,subprocess,sys,tarfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
checkpoint=json.loads((P/'recovery-checkpoint-016.json').read_text())
foundation=json.loads((P/'foundation-colocated-recovery-checkpoint-016-v1.json').read_text())
assert foundation['opaque_direct_inputs_restored_and_hash_mode_verified']==420
root=Path(checkpoint['restored_root']).resolve();assert root.is_relative_to(Path('/private/tmp'))
supplement=json.loads((P/'own-source-recovery-supplement-v2.json').read_text())
archive=root/supplement['archive'];manifest=root/supplement['manifest']
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(archive)==supplement['archive_sha256']and sha(manifest)==supplement['manifest_sha256']
entries=json.loads(manifest.read_text())['files'];added=[];matching=[]
with tarfile.open(archive)as tar:
 members=tar.getmembers();assert len(members)==len(entries)==13
 for member,row in zip(members,entries,strict=True):
  relative=Path(member.name);assert member.isfile()and member.name==row['path']and not relative.is_absolute()and'..'not in relative.parts
  target=root/relative;assert not target.is_symlink()
  if target.exists():
   assert sha(target)==row['sha256']and stat.S_IMODE(target.stat().st_mode)==row['mode'];matching.append(row['path']);continue
  target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb')as stream:stream.write(tar.extractfile(member).read())
  os.chmod(target,row['mode']);assert sha(target)==row['sha256']and stat.S_IMODE(target.stat().st_mode)==row['mode'];added.append(row['path'])
assert len(added)==11 and len(matching)==2
observer=root/P.relative_to(ROOT)/'observe_restored_own_modules_v1.py'
assert sha(observer)==sha(P/'observe_restored_own_modules_v1.py')
command=[sys.executable,'-B',str(observer)];out=subprocess.run(command,cwd=root,capture_output=True,timeout=20)
assert out.returncode==0,out.stderr.decode();observed=json.loads(out.stdout)
assert len(observed['module_paths'])==6 and all(Path(path).is_relative_to(root)for path in observed['module_paths'])
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checkpoint':16,
 'checkpoint_receipt_sha256':sha(P/'recovery-checkpoint-016.json'),'restored_root':str(root),
 'foundation_direct_inputs':420,'supplement_source_test_files':13,'existing_matches_no_overwrite':matching,
 'new_distinct_files_restored_and_hash_mode_verified':added,'combined_distinct_selected_inputs':431,
 'restored_own_module_import_command':command,'restored_own_module_import_observation':observed,
 'private_eval_body_semantic_decoding':False,'helper_dispatched':False,'suite_reruns':0,
 'limits':'Currentresearch+431selectedinputscolocated,6ownmodulesimported,2ownedGobinariesreplayedseparately. Notalltransitiveapps/frontend/Ruby/Gohelper/model/nativeframeworkorfullstaterecovery; no cleanclone/remote/powerloss/Windowsproof.',
 'production_changes':0,'model_calls':0,'gold':0,'optimizer_updates':0}
with(P/'final-colocated-source-recovery-v1.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
copy=ROOT/'.local-backups/acceptance-calibration-20261121/checkpoint-016/final-colocated-source-recovery-receipt.json'
with copy.open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
os.chmod(copy,0o600)
print(json.dumps({k:v for k,v in result.items()if k not in ['restored_own_module_import_command','restored_own_module_import_observation']},indent=2))
