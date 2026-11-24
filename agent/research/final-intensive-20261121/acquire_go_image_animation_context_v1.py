import json,subprocess,os,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];ledger=json.loads((p/'repository-action-ledger-v7.json').read_text());repo=Path(next(r['absolute_path'] for r in ledger['records'] if r['repository']=='go-image-optimizer'));rev='48476de6e4450294b7769ab7af90805100bb21b5';folder=p/'go-image-animation-source-context-v1';folder.mkdir();commands=[]
env={**os.environ,'GIT_OPTIONAL_LOCKS':'0','GIT_NO_LAZY_FETCH':'1'}
def run(argv):
 cmd=['git','--no-optional-locks','-C',str(repo)]+argv;r=subprocess.run(cmd,capture_output=True,env=env,timeout=30);commands.append({'command':cmd,'exit_code':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()});assert r.returncode==0;return r.stdout
hits=run(['grep','-n','-e','ValidateAnimatedDimensions','-e','DefaultMaxAnimatedFramePixels',rev,'--','*.go']).decode();paths=sorted({line.split(':',2)[1] for line in hits.splitlines()});paths+=['LICENSE','backend/go.mod'];records=[]
for name in sorted(set(paths)):
 raw=run(['show',rev+':'+name]);target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);target.open('xb').write(raw);records.append({'source_path':name,'saved_path':str(target.relative_to(root)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':rev,'commands':commands,'records':records,'scope':'Lexical same-revision Go callers/declarations and tests; not dynamic exhaustive caller graph or runtime execution','external_files_changed':False}
with (p/'go-image-animation-context-acquisition-v1.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'paths':paths,'files':len(records),'grep':hits}))
