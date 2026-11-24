"""Source-only minimum-version Module traversal reference; not an installed framework pin."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;repo='ml-explore/mlx';tag='v0.32.3'
def get(url,limit):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(limit+1)
 assert len(raw)<=limit
 return raw
raw=get('https://api.github.com/repos/'+repo+'/git/ref/tags/'+tag,65536)
with(P/'mlx-v0.32.3-ref-v1.json').open('xb')as f:f.write(raw)
obj=json.loads(raw)['object']
if obj['type']=='tag':
 raw=get(obj['url'],65536)
 with(P/'mlx-v0.32.3-tag-v1.json').open('xb')as f:f.write(raw)
 obj=json.loads(raw)['object']
assert obj['type']=='commit';revision=obj['sha'];raw=get('https://api.github.com/repos/'+repo+'/git/trees/'+revision+'?recursive=1',1048576);tree=json.loads(raw);assert tree['truncated']is False
with(P/'mlx-v0.32.3-tree-v1.json').open('xb')as f:f.write(raw)
paths=['python/mlx/nn/layers/base.py','LICENSE'];entries=[e for e in tree['tree']if e['path']in paths];assert len(entries)==len(paths)and all(e['type']=='blob'and e['mode']=='100644'and e['size']<=131072 for e in entries)
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':repo,'tag':tag,'revision':revision,'selected_blobs':entries,'tree_sha256':hashlib.sha256(raw).hexdigest(),'hypothesis':'Inspect named module traversal semantics needed to bound theoretical LoRA key selection in the pinned MLX-LM helper.','scope':'MLX-LM pyproject requiresmlx>=0.32.3onDarwin;thissourcecutisone minimum-version reference,not the actual installed/resolved framework (none installed).','source_bodies_fetched':False,'source_execution_allowed':False,'framework_installation_allowed':False,'weights_or_tokenizers_requested':False,'training_steps':0,'owner_approved':False,'training_excluded':True}
with(P/'mlx-module-source-scope-freeze-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'tag':tag,'revision':revision,'selected_source_files':len(entries)})
