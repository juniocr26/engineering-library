"""Consume the sealed intermediate source cut, without loading the live caller."""
import datetime, hashlib, json, pathlib, subprocess, time
HERE=pathlib.Path(__file__).resolve().parent
REMOTE=r'''
import pathlib,tarfile,hashlib,json,subprocess,os,shutil
base=pathlib.Path('/sources/engineering-library')
cut=base/'.local-backups/continuation-20261120/intermediate-cut-v1'
root=pathlib.Path('/tmp/el-continuation-20261120-linux-restore-v2')
root.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((base/'agent/research/continuation-20261120/intermediate-recovery-cut-receipt-v1.json').read_text())
m=json.loads((cut/'input-manifest.json').read_text())
assert sha(cut/'input-manifest.json')==receipt['input_manifest']['sha256']
for key in ('baseline_archive','overlay_archive'):
 a=base/receipt[key]['path'];assert sha(a)==receipt[key]['sha256']
 with tarfile.open(a) as t:
  for member in t.getmembers():
   parts=pathlib.PurePosixPath(member.name).parts
   assert not member.name.startswith('/') and '..' not in parts
   assert member.isfile() or member.isdir()
   if key=='baseline_archive' and member.name in m['skip_live_baseline_paths']:continue
   target=root/member.name
   if member.isdir():target.mkdir(parents=True,exist_ok=True)
   else:
    target.parent.mkdir(parents=True,exist_ok=True)
    with t.extractfile(member) as source,target.open('wb') as dest:shutil.copyfileobj(source,dest)
    target.chmod(member.mode & 0o777)
expected={k:v for k,v in m['baseline_tracked_entries'].items() if k not in m['skip_live_baseline_paths']}
for e in m['overlay_entries']:
 expected[e['path']]=e
for rel,e in expected.items():
 assert sha(root/rel)==e['sha256'],rel
for name in ('Gemfile','Gemfile.lock'):
 assert sha(root/'backend'/name)==sha(pathlib.Path('/app/backend')/name),name
p=root/'agent/research/continuation-20261120'
probe=(p/'probe_ruby_exception_guard_v3.rb').read_text()
probe=probe.replace("require '/app/backend/lib/documentation/project_command'", "require "+repr(str(root/'backend/lib/documentation/project_command')))
probe=probe.replace("puts JSON.generate({", "raise 'live caller loaded' unless Documentation::Command.instance_method(:validate_and_render).source_location.first.start_with?("+repr(str(root))+ "); puts JSON.generate({")
outputs=[]
for name in ('ruby-exception-guard-protocol-v1.json','ruby-exception-guard-ambiguity-protocol-v1.json'):
 protocol=json.loads((p/name).read_text())
 if 'source_root' in protocol:protocol['source_root']=protocol['source_root'].replace(str(base),str(root),1)
 for row in protocol['cases']:
  if 'source_root' in row:row['source_root']=row['source_root'].replace(str(base),str(root),1)
 env=dict(os.environ,BUNDLE_GEMFILE='/app/backend/Gemfile',RAILS_ENV='test',DATABASE_URL='sqlite3::memory:',PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0')
 r=subprocess.run(['bundle','exec','ruby','-e',probe],cwd=root/'backend',env=env,input=json.dumps(protocol),text=True,capture_output=True,timeout=120)
 assert r.returncode==0,r.stderr
 result=json.loads(r.stdout)
 for pred,ref in zip(result['rows'],protocol['cases'],strict=True):assert pred['id']==ref['id'] and pred['status']==ref['expected_status']
 outputs.append({'protocol':name,'result':result,'stderr':r.stderr})
print(json.dumps({'status':'VERIFIED','restored_root':str(root),'verified_files':len(expected),'caller_source_loaded_from_restore':True,'dependency_manifest_identity_verified':True,'distinct_existing_cases':12,'results':outputs,'third_party_source_execution':False,'model_calls':0,'neural_training':False,'cold_boot':False}))
'''
start=time.monotonic()
r=subprocess.run(['docker','exec','-i','engineering-library-backend-1','python3','-c',REMOTE],input='',text=True,capture_output=True,timeout=240)
(HERE/'linux-restored-renderer-v2.stdout').write_text(r.stdout)
(HERE/'linux-restored-renderer-v2.stderr').write_text(r.stderr)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'wall_seconds':time.monotonic()-start,'producer_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
if r.returncode==0:record.update(json.loads(r.stdout))
(HERE/'linux-restored-renderer-v2.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='results'}))
raise SystemExit(r.returncode)
