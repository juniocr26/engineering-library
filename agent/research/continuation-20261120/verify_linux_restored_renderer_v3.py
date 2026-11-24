"""Restore current 1.9.43 source and exercise real consumers from that tree."""
import datetime,hashlib,json,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent
REMOTE=r'''
import hashlib,json,os,pathlib,shutil,subprocess,sys,tarfile
base=pathlib.Path('/sources/engineering-library');p=base/'agent/research/continuation-20261120';receipt=json.loads((p/'recovery-delta-receipt-v3.json').read_text());root=pathlib.Path('/tmp/el-continuation-20261120-linux-restore-v3');root.mkdir(exist_ok=False)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
manifest_path=base/receipt['input_manifest']['path'];assert sha(manifest_path)==receipt['input_manifest']['sha256'];manifest=json.loads(manifest_path.read_text())
archives=[]
for asset in receipt['parent_assets']:
 path=base/asset['path'];assert sha(path)==asset['sha256']
 if asset['role']in ['baseline_archive','overlay_archive']:archives.append((asset['role'],path))
 else:
  target=root/asset['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
asset=receipt['delta_archive'];path=base/asset['path'];assert sha(path)==asset['sha256'];archives.append(('current_delta',path))
for role,archive in archives:
 with tarfile.open(archive)as tar:
  for member in tar.getmembers():
   rel=pathlib.PurePosixPath(member.name);assert not rel.is_absolute()and'..'not in rel.parts and(member.isfile()or member.isdir())
   if role=='baseline_archive'and member.name in manifest['skip_live_baseline_paths']:continue
   target=root/member.name
   if member.isdir():target.mkdir(parents=True,exist_ok=True)
   else:
    target.parent.mkdir(parents=True,exist_ok=True)
    with tar.extractfile(member)as source,target.open('wb')as dest:shutil.copyfileobj(source,dest)
    target.chmod(member.mode&0o777)
for name,expected in manifest['effective_expected_files'].items():assert sha(root/name)==expected['sha256'],name
for name in ['Gemfile','Gemfile.lock']:assert sha(root/'backend'/name)==sha(pathlib.Path('/app/backend')/name)
restored_p=root/'agent/research/continuation-20261120'
outputs=[]
for probe_name,protocol_names in [('probe_ruby_exception_guard_v3.rb',['ruby-exception-guard-protocol-v1.json','ruby-exception-guard-ambiguity-protocol-v1.json']),('probe_returned_map_renderer_v1.rb',['returned-map-guard-control-oracle-v2.json'])]:
 probe=(restored_p/probe_name).read_text().replace("require '/app/backend/lib/documentation/project_command'",'require '+repr(str(root/'backend/lib/documentation/project_command')))
 probe=probe.replace('puts JSON.generate({',"raise 'live caller loaded' unless Documentation::Command.instance_method(:validate_and_render).source_location.first.start_with?("+repr(str(root))+'); puts JSON.generate({')
 for protocol_name in protocol_names:
  protocol=json.loads((restored_p/protocol_name).read_text())
  if 'source_root'in protocol:protocol['source_root']=protocol['source_root'].replace(str(base),str(root),1)
  for row in protocol['cases']:
   if 'source_root'in row:row['source_root']=row['source_root'].replace(str(base),str(root),1)
  env=dict(os.environ,BUNDLE_GEMFILE='/app/backend/Gemfile',RAILS_ENV='test',DATABASE_URL='sqlite3::memory:',PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0')
  r=subprocess.run(['bundle','exec','ruby','-e',probe],cwd=root/'backend',env=env,input=json.dumps(protocol),capture_output=True,text=True,timeout=90)
  assert r.returncode==0,r.stderr;result=json.loads(r.stdout);assert result['caller_version']=='1.9.43'
  for pred,ref in zip(result['rows'],protocol['cases']):assert pred['id']==ref['id']and pred['status']==ref['expected_status']
  outputs.append({'protocol':protocol_name,'result':result,'stderr':r.stderr})
bootstrap=subprocess.run([sys.executable,str(root/'agent/recovery/bootstrap.py'),'knowledge'],cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True,timeout=60);assert bootstrap.returncode==0,bootstrap.stderr
for name,expected in manifest['effective_expected_files'].items():assert sha(root/name)==expected['sha256'],name
print(json.dumps({'status':'VERIFIED','restored_root':str(root),'caller':'1.9.43','expected_files':len(manifest['effective_expected_files']),'all_expected_hashes_unchanged':True,'restored_bootstrap':json.loads(bootstrap.stdout),'caller_source_loaded_from_restore':True,'dependency_manifest_identity_verified':True,'distinct_existing_renderer_cases':sum(len(r['result']['rows'])for r in outputs),'known_semantic_limit_rows_preserved':6,'results':outputs,'new_distinct_cases':0,'public_source_or_neural_experiments_rerun':False,'cold_boot_or_remote_durability':False}))
'''
start=time.monotonic();r=subprocess.run(['docker','exec','-i','engineering-library-backend-1','python3','-c',REMOTE],capture_output=True,text=True,timeout=240)
(P/'linux-restored-renderer-v3.stdout').write_text(r.stdout);(P/'linux-restored-renderer-v3.stderr').write_text(r.stderr)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'wall_seconds':time.monotonic()-start,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
if r.returncode==0:record.update(json.loads(r.stdout))
with(P/'linux-restored-renderer-v3.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print({k:v for k,v in record.items()if k!='results'});raise SystemExit(r.returncode)
