"""Follow exact pinned Git tree to source declarations and maintainer prose."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;rev='4b071d3e54d466a4059de89006c752da782c8b02';base=P/'new-public-sources-v1/lukeed--totalist'/rev
tree=json.loads((P/'totalist-revision-tree-v1.json').read_text());rows=[]
for e in tree['tree']:
 if e['path']not in ['src/async.d.ts','src/sync.d.ts','readme.md']:continue
 url='https://raw.githubusercontent.com/lukeed/totalist/'+rev+'/'+e['path']
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as r:raw=r.read(65537)
 assert len(raw)<=65536 and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['sha']
 dest=base/e['path'];dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('xb')as f:f.write(raw)
 rows.append({'path':e['path'],'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob':e['sha'],'tree_blob_matches':True})
with(P/'totalist-declared-types-provenance-v1.json').open('x')as f:f.write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':rev,'rows':rows,'source_executed':False,'build_executed':False,'package_installed':False},indent=2)+'\n')
print(json.dumps({'files':len(rows),'bytes':sum(r['bytes']for r in rows)}))
