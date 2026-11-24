from pathlib import Path
import json,hashlib,datetime,subprocess,os
p=Path(__file__).resolve().parent;root=p.parents[2];d=json.loads((p/'opencv-targets-source-protocol-v1.json').read_text());ledger=json.loads((p/'repository-action-ledger-v14.json').read_text());repo=next(x['absolute_path'] for x in ledger['records'] if x['repository']=='opencv');out=p/'opencv-targets-source-context-v1';out.mkdir();records=[]
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',GIT_NO_LAZY_FETCH='1')
for path in d['source_paths']:
 cmd=['git','--no-optional-locks','-C',repo,'show',d['revision']+':'+path];r=subprocess.run(cmd,env=env,capture_output=True);rec={'command':cmd,'exit_code':r.returncode,'stderr':r.stderr.decode(errors='replace')}
 if r.returncode==0:
  f=out/path;f.parent.mkdir(parents=True,exist_ok=True)
  with f.open('xb') as stream:stream.write(r.stdout)
  rec.update(saved_path=str(f.relative_to(root)),sha256=hashlib.sha256(r.stdout).hexdigest(),bytes=len(r.stdout))
 records.append(rec)
with (p/'opencv-targets-source-acquisition-v1.json').open('x') as f:json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'read_only':True,'source_program_executed':False},f,indent=2);f.write('\n')
print(json.dumps([{'path':r['command'][-1],'exit':r['exit_code'],'bytes':r.get('bytes')} for r in records]))
