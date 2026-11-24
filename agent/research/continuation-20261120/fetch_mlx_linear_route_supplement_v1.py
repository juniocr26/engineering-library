"""Resolve hasattr(to_lora) route statically before using fallback adapter dimensions."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;tree=json.loads((P/'mlx-v0.32.3-tree-v1.json').read_text());revision='64ea011cb65f14d9ce2737e60db9a4ae91ed7441';paths=['python/mlx/nn/layers/linear.py','python/mlx/nn/layers/quantized.py'];entries=[e for e in tree['tree']if e['path']in paths];assert len(entries)==2 and all(e['mode']=='100644'and e['size']<=32768 for e in entries)
protocol={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':'ml-explore/mlx','revision':revision,'selected_blobs':entries,'reason':'Pinned MLX-LM prefers a layer.to_lora method before its fallback LoRALinear. Inspect minimum-version Linear/QuantizedLinear definitions/inheritance rather than assume the fallback applies.','source_bodies_fetched':False,'source_execution_allowed':False,'framework_import_allowed':False,'training_steps':0}
with(P/'mlx-linear-route-supplement-protocol-v1.json').open('x')as f:f.write(json.dumps(protocol,indent=2)+'\n')
rows=[]
for e in entries:
 url='https://raw.githubusercontent.com/ml-explore/mlx/'+revision+'/'+e['path']
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EngineeringLibrarySourceResearch/1.0'}),timeout=35)as response:raw=response.read(32769)
 assert len(raw)==e['size']and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['sha'];path=P/'new-public-sources-v1/ml-explore--mlx'/revision/e['path']
 with path.open('xb')as f:f.write(raw)
 rows.append({'path':str(path.relative_to(P)),'upstream_path':e['path'],'revision':revision,'git_blob':e['sha'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,'all_git_blobs_verified':True,'source_executed':False,'framework_imported':False,'training_steps':0,'owner_approved':False,'training_excluded':True}
with(P/'mlx-linear-route-supplement-receipt-v1.json').open('x')as f:f.write(json.dumps(r,indent=2)+'\n')
print({'source_files':2,'bytes':sum(e['bytes']for e in rows)})
