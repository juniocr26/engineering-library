"""Freeze a new Go retry-adapter family before selected source bodies are fetched."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];baseline=json.loads((P/'baseline.json').read_text());hits=[];scanned=0
for name in baseline['tracked_identity']:
 f=ROOT/name
 if not f.is_file()or f.stat().st_size>1048576:continue
 raw=f.read_bytes()
 if b'\0'in raw:continue
 try:text=raw.decode()
 except UnicodeDecodeError:continue
 scanned+=1
 for number,line in enumerate(text.splitlines(),1):
  if'cenkalti/backoff'in line.casefold():hits.append({'path':name,'line':number,'line_sha256':hashlib.sha256(line.encode()).hexdigest()})
exposure={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tracked_utf8_files_le1mib':scanned,'explicit_repository_name_hits':hits,'private_text_snippets_not_copied':True,'limits':'No claim about ignored dependencies, model pretraining or pristine neural holdout.'}
with(P/'backoff-prior-exposure-v1.json').open('x')as f:f.write(json.dumps(exposure,indent=2)+'\n')
def get(url,limit):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(limit+1)
 assert len(raw)<=limit
 return raw
rows=[];repo='cenkalti/backoff'
for tag in ['v4.1.3','v4.3.0']:
 raw=get('https://api.github.com/repos/'+repo+'/git/ref/tags/'+tag,65536)
 with(P/('backoff-'+tag+'-ref-v1.json')).open('xb')as f:f.write(raw)
 obj=json.loads(raw)['object']
 if obj['type']=='tag':
  raw=get(obj['url'],65536)
  with(P/('backoff-'+tag+'-tag-v1.json')).open('xb')as f:f.write(raw)
  obj=json.loads(raw)['object']
 assert obj['type']=='commit';rev=obj['sha'];raw=get('https://api.github.com/repos/'+repo+'/git/trees/'+rev+'?recursive=1',1048576);tree=json.loads(raw);assert tree['truncated']is False
 with(P/('backoff-'+tag+'-tree-v1.json')).open('xb')as f:f.write(raw)
 selected=[e for e in tree['tree']if e['type']=='blob'and'/'not in e['path']and((e['path'].endswith('.go')and not e['path'].endswith('_test.go'))or e['path']in ['go.mod','go.sum','LICENSE'])];assert any(e['path']=='retry.go'for e in selected)and any(e['path']=='LICENSE'for e in selected);assert all(e['size']<=65536 and e['mode']=='100644'for e in selected)
 rows.append({'repository':repo,'tag':tag,'revision':rev,'selected_blobs':selected,'tree_sha256':hashlib.sha256(raw).hexdigest()})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':repo,'cuts':rows,'prior_exposure':'backoff-prior-exposure-v1.json','hypothesis':'Cross-file retry/context/permanent-error adapters may invalidate naive claims about attempts, cancellation, notification and delay. Review source first, then freeze safe synthetic observations or preserve static-only boundary.','selected_source_bodies_fetched':False,'source_execution_allowed_at_this_stage':False,'packages_or_toolchains_installed':False,'training_excluded':True,'owner_approved':False,'certified_neural_holdout':False,'model_calls':0}
with(P/'backoff-source-family-freeze-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'cuts':[(c['tag'],c['revision'],len(c['selected_blobs']))for c in rows],'prior_name_hits':len(hits)})
