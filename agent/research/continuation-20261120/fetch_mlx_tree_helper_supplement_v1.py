"""Follow one statically required module-path dependency; no source execution."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;tree=json.loads((P/'mlx-v0.32.3-tree-v1.json').read_text());entry=next(e for e in tree['tree']if e['path']=='python/mlx/utils.py');revision='64ea011cb65f14d9ce2737e60db9a4ae91ed7441';assert entry['size']<=32768 and entry['mode']=='100644'
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':'ml-explore/mlx','revision':revision,'selected_blob':entry,'reason':'Module.apply_to_modules delegates path formation to imported tree_flatten. Read that complete source dependency before claiming exact default-vs-global matching semantics.','source_body_fetched':False,'source_execution_allowed':False,'framework_import_allowed':False,'training_steps':0}
with(P/'mlx-tree-helper-supplement-protocol-v1.json').open('x')as f:f.write(json.dumps(protocol,indent=2)+'\n')
url='https://raw.githubusercontent.com/ml-explore/mlx/'+revision+'/'+entry['path']
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(32769)
assert len(raw)==entry['size']and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['sha'];path=P/'new-public-sources-v1/ml-explore--mlx'/revision/entry['path']
with path.open('xb')as f:f.write(raw)
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path':str(path.relative_to(P)),'upstream_path':entry['path'],'revision':revision,'git_blob':entry['sha'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'source_executed':False,'framework_imported':False,'packages_installed':False,'training_steps':0,'owner_approved':False,'training_excluded':True}
with(P/'mlx-tree-helper-supplement-receipt-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'verified_bytes':len(raw),'source_executed':False})
