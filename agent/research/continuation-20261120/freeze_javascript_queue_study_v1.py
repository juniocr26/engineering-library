"""Freeze source families and metadata before selected source bodies are seen."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
baseline=json.loads((P/'baseline.json').read_text());hits=[];inspected=0
for name,entry in baseline['tracked_identity'].items():
 path=ROOT/name
 if not path.is_file()or path.stat().st_size>1048576:continue
 raw=path.read_bytes()
 if b'\0'in raw:continue
 try:text=raw.decode()
 except UnicodeDecodeError:continue
 inspected+=1
 for i,line in enumerate(text.splitlines(),1):
  if any(term in line.casefold()for term in ['p-limit','yocto-queue']):hits.append({'path':name,'line':i,'text':line[:400]})
exposure={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_text_files_inspected':inspected,'hits':hits,'limits':'Baseline tracked UTF-8 files <=1MiB only; ignored archives/dependency trees/model memory not certified absent. Names in lockfiles are exposure, not source body execution.','certified_neural_holdout':False,'training_excluded':True}
with(P/'javascript-queue-prior-exposure-v1.json').open('x')as f:f.write(json.dumps(exposure,indent=2)+'\n')
def get(url,limit):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as r:raw=r.read(limit+1)
 assert len(raw)<=limit
 return raw
records=[]
for repo,tag in [('sindresorhus/p-limit','v4.0.0'),('sindresorhus/yocto-queue','v1.0.0')]:
 prefix=repo.replace('/','--');raw=get('https://api.github.com/repos/'+repo+'/git/ref/tags/'+tag,65536)
 with(P/(prefix+'-ref-v1.json')).open('xb')as f:f.write(raw)
 obj=json.loads(raw)['object']
 if obj['type']=='tag':
  raw=get(obj['url'],65536)
  with(P/(prefix+'-tag-v1.json')).open('xb')as f:f.write(raw)
  obj=json.loads(raw)['object']
 assert obj['type']=='commit';rev=obj['sha'];raw=get('https://api.github.com/repos/'+repo+'/git/trees/'+rev+'?recursive=1',1048576);tree=json.loads(raw);assert tree['truncated']is False
 with(P/(prefix+'-tree-v1.json')).open('xb')as f:f.write(raw)
 desired={'index.js','index.d.ts','package.json','license'};entries=[e for e in tree['tree']if e['type']=='blob'and e['path']in desired];assert len(entries)==4
 records.append({'repository':repo,'tag':tag,'revision':rev,'selected_blobs':entries,'tree_sha256':hashlib.sha256(raw).hexdigest()})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repositories':records,'purpose':'Study exact concurrency-limiter and queue source dependency, typed declarations and promise scheduling with a new source pair. No source bodies inspected at this freeze.','target_bodies_fetched':False,'prior_exposure_scan':'javascript-queue-prior-exposure-v1.json','certified_neural_holdout':False,'dependency_ancestry':'The queue is a direct declared dependency of the limiter; the two repositories are related and cannot be counted as independent source families for the composed task.','source_execution_allowed_at_this_stage':False,'training_excluded':True,'packages_installed':False,'model_calls':0}
with(P/'javascript-queue-source-freeze-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'source_pairs':[(r['repository'],r['revision'])for r in records],'prior_exposure_hits':len(hits),'bodies_fetched':False})
