import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent

def get(url,limit):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(limit+1)
 assert len(raw)<=limit
 return raw
rows=[]
for repo,tag in [('sindresorhus/p-limit','v3.1.0'),('sindresorhus/yocto-queue','v0.1.0')]:
 name=repo.replace('/','--');raw=get('https://api.github.com/repos/'+repo+'/git/ref/tags/'+tag,65536)
 with(P/(name+'-historical-ref-v1.json')).open('xb')as f:f.write(raw)
 obj=json.loads(raw)['object']
 if obj['type']=='tag':
  raw=get(obj['url'],65536)
  with(P/(name+'-historical-tag-v1.json')).open('xb')as f:f.write(raw)
  obj=json.loads(raw)['object']
 assert obj['type']=='commit';revision=obj['sha'];raw=get('https://api.github.com/repos/'+repo+'/git/trees/'+revision+'?recursive=1',1048576);tree=json.loads(raw);assert tree['truncated']is False
 with(P/(name+'-historical-tree-v1.json')).open('xb')as f:f.write(raw)
 entries=[e for e in tree['tree']if e['type']=='blob'and e['path']in {'index.js','index.d.ts','package.json','license'}];assert len(entries)==4
 rows.append({'repository':repo,'tag':tag,'revision':revision,'selected_blobs':entries,'tree_sha256':hashlib.sha256(raw).hexdigest()})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cuts':rows,'purpose':'Compare actual older package/source contracts with the already exposed ESM cuts, especially formal-signatureNOOP versus manifest/export/dependencychanges.','bodies_fetched':False,'source_execution_allowed_at_this_stage':False,'already_development_exposed_source_family':True,'related_dependency_group':True,'not_new_independent_family':True,'training_excluded':True,'model_calls':0}
with(P/'javascript-queue-historical-freeze-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'revisions':[(r['repository'],r['revision'])for r in rows],'bodies_fetched':False})
