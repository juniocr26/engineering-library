"""Preserve a pinned public tree and package contract files, without install/build."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;repo='lukeed/totalist';rev='4b071d3e54d466a4059de89006c752da782c8b02';base=P/'new-public-sources-v1/lukeed--totalist'/rev

def get(url,limit):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as r:
  raw=r.read(limit+1)
 if len(raw)>limit:raise ValueError('bounded source response exceeded')
 return raw
url='https://api.github.com/repos/'+repo+'/git/trees/'+rev+'?recursive=1'
raw=get(url,262144);tree=json.loads(raw);assert tree.get('truncated')is False
with(P/'totalist-revision-tree-v1.json').open('xb')as f:f.write(raw)
entries=[e for e in tree['tree']if e['type']=='blob'and e['path']in ('index.d.ts','sync.d.ts','bundt.config.js','package.json','src/async.js','src/sync.js','license')]
rows=[]
for e in entries:
 path=base/e['path'];origin='existing'if path.exists()else'new';url='https://raw.githubusercontent.com/'+repo+'/'+rev+'/'+e['path']
 raw=path.read_bytes()if path.exists()else get(url,65536)
 blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob==e['sha']
 if not path.exists():
  path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('xb')as f:f.write(raw)
 rows.append({'path':e['path'],'url':url,'origin':origin,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob':blob,'tree_blob_matches':True})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':repo,'revision':rev,'tree_url':'https://api.github.com/repos/'+repo+'/git/trees/'+rev+'?recursive=1','tree_sha256':hashlib.sha256((P/'totalist-revision-tree-v1.json').read_bytes()).hexdigest(),'rows':rows,'matching_distribution_paths_in_tree':[e['path']for e in tree['tree']if e['path'].startswith(('dist/','sync/'))],'source_executed':False,'build_executed':False,'package_installed':False,'registry_tarball_authenticated':False,'neural_training':False}
with(P/'totalist-package-contract-provenance-v1.json').open('x')as f:f.write(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
