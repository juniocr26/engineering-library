"""New Go byte-unit family: freeze metadata/exposure before selected bodies."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];baseline=json.loads((P/'baseline.json').read_text());hits=[];scanned=0
for name,entry in baseline['tracked_identity'].items():
 path=ROOT/name
 if not path.is_file()or path.stat().st_size>1048576:continue
 raw=path.read_bytes()
 if b'\0'in raw:continue
 try:text=raw.decode()
 except UnicodeDecodeError:continue
 scanned+=1
 for number,line in enumerate(text.splitlines(),1):
  if'dustin/go-humanize'in line.lower()or'go-humanize'in line.lower():hits.append({'path':name,'line':number,'line_sha256':hashlib.sha256(line.encode()).hexdigest()})
exposure={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_text_files':scanned,'name_hits':hits,'private_text_snippets_not_copied':True,'limits':'BaselineUTF8trackedfiles<=1MiBonly;noignoreddependencyarchiveormodel-pretrainingindependencecertification.','training_excluded':True}
with(P/'humanize-prior-exposure-v1.json').open('x')as f:f.write(json.dumps(exposure,indent=2)+'\n')
def get(url,limit):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(limit+1)
 if len(raw)>limit:raise ValueError('public metadata bound')
 return raw
repo='dustin/go-humanize';rows=[]
for tag in ['v1.0.0','v1.0.1']:
 raw=get('https://api.github.com/repos/'+repo+'/git/ref/tags/'+tag,65536)
 with(P/('humanize-'+tag+'-ref-v1.json')).open('xb')as f:f.write(raw)
 obj=json.loads(raw)['object']
 if obj['type']=='tag':
  raw=get(obj['url'],65536)
  with(P/('humanize-'+tag+'-tag-v1.json')).open('xb')as f:f.write(raw)
  obj=json.loads(raw)['object']
 assert obj['type']=='commit';revision=obj['sha'];raw=get('https://api.github.com/repos/'+repo+'/git/trees/'+revision+'?recursive=1',1048576);tree=json.loads(raw);assert tree['truncated']is False
 with(P/('humanize-'+tag+'-tree-v1.json')).open('xb')as f:f.write(raw)
 entries=[e for e in tree['tree']if e['type']=='blob'and'/'not in e['path']and((e['path'].endswith('.go')and not e['path'].endswith('_test.go'))or e['path']in ['go.mod','LICENSE'])];assert entries and any(e['path']=='bytes.go'for e in entries)and any(e['path']=='LICENSE'for e in entries)
 rows.append({'repository':repo,'tag':tag,'revision':revision,'selected_blobs':entries,'tree_sha256':hashlib.sha256(raw).hexdigest()})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':repo,'cuts':rows,'purpose':'Source-groundeddecimal/binarybyte-unitandparse/formatcontracts;potentialcompilerconstantandboundedsyntheticruntimeobservationsafterseparatesourcereview.','target_source_bodies_fetched':False,'source_execution_allowed_at_this_stage':False,'prior_exposure_scan':'humanize-prior-exposure-v1.json','not_certified_neural_holdout':True,'training_excluded':True,'owner_approved':False,'packages_installed':False,'model_calls':0}
with(P/'humanize-source-family-freeze-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'cuts':[(r['tag'],r['revision'],len(r['selected_blobs']))for r in rows],'prior_name_hits':len(hits),'source_bodies_fetched':False})
